import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo.errors import DuplicateKeyError
from app.database.connection import db_connection
from app.core.config import settings
from app.core.logger import logger
from app.utils.exceptions import DuplicateConversationIdException

# Valid lifecycle status values
CONVERSATION_STATUS_ACTIVE   = "active"
CONVERSATION_STATUS_ARCHIVED = "archived"
CONVERSATION_STATUS_DELETED  = "deleted"

# Statuses considered "visible" in normal list/search queries
VISIBLE_STATUSES = [CONVERSATION_STATUS_ACTIVE, CONVERSATION_STATUS_ARCHIVED]


class ConversationRepository:
    """
    MongoDB CRUD Repository for Conversation Documents.
    Pure database operations only. No business logic.
    Collection: CONVERSATION_COLLECTION

    Soft Delete Policy:
        ACTIVE   — default state for all new conversations
        ARCHIVED — conversation kept for records but no longer active
        DELETED  — soft deleted; excluded from all list/search queries
                   Real MongoDB document is NEVER permanently removed.
    """

    def _collection(self):
        return db_connection.get_collection(settings.CONVERSATION_COLLECTION)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def insert_one(
        self,
        conversation_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Inserts a new conversation document with status=ACTIVE."""
        now = datetime.utcnow().isoformat()
        merged_metadata = dict(metadata or {})
        if user_id:
            merged_metadata["userId"] = user_id
        doc = {
            "conversation_id": conversation_id,
            "created_at":      now,
            "updated_at":      now,
            "deleted_at":      None,
            "status":          CONVERSATION_STATUS_ACTIVE,
            "metadata":        merged_metadata
        }
        col = self._collection()
        if col is not None:
            try:
                await col.insert_one({**doc})
            except DuplicateKeyError:
                raise DuplicateConversationIdException(conversation_id)
            logger.info(f"[ConversationRepo] Inserted conversation '{conversation_id}' [status=active]")
        return doc

    async def update_timestamp(self, conversation_id: str) -> bool:
        """Updates the updatedAt timestamp on an existing conversation document."""
        col = self._collection()
        if col is not None:
            result = await col.update_one(
                {"conversation_id": conversation_id},
                {"$set": {"updated_at": datetime.utcnow().isoformat()}}
            )
            return result.modified_count > 0
        return False

    async def update_status(self, conversation_id: str, status: str) -> bool:
        """Updates the status field of a conversation document."""
        col = self._collection()
        if col is not None:
            result = await col.update_one(
                {"conversation_id": conversation_id},
                {"$set": {
                    "status":     status,
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            return result.modified_count > 0
        return False

    async def soft_delete(self, conversation_id: str) -> bool:
        """
        Soft deletes a conversation by setting status=DELETED and recording deletedAt.
        The MongoDB document is NEVER permanently removed.
        Conversations with status=DELETED are excluded from all list/search queries.
        """
        col = self._collection()
        if col is not None:
            result = await col.update_one(
                {"conversation_id": conversation_id},
                {"$set": {
                    "status":     CONVERSATION_STATUS_DELETED,
                    "deleted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            deleted = result.modified_count > 0
            if deleted:
                logger.info(
                    f"[ConversationRepo] Soft-deleted conversation '{conversation_id}' "
                    f"[status=deleted]"
                )
            return deleted
        return False

    async def archive(self, conversation_id: str) -> bool:
        """
        Archives a conversation by setting status=ARCHIVED.
        Archived conversations remain visible in list/search queries.
        """
        col = self._collection()
        if col is not None:
            result = await col.update_one(
                {"conversation_id": conversation_id},
                {"$set": {
                    "status":     CONVERSATION_STATUS_ARCHIVED,
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            archived = result.modified_count > 0
            if archived:
                logger.info(
                    f"[ConversationRepo] Archived conversation '{conversation_id}' "
                    f"[status=archived]"
                )
            return archived
        return False

    async def restore(self, conversation_id: str) -> bool:
        """
        Restores a DELETED or ARCHIVED conversation back to ACTIVE status.
        """
        col = self._collection()
        if col is not None:
            result = await col.update_one(
                {"conversation_id": conversation_id},
                {"$set": {
                    "status":     CONVERSATION_STATUS_ACTIVE,
                    "deleted_at": None,
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            restored = result.modified_count > 0
            if restored:
                logger.info(
                    f"[ConversationRepo] Restored conversation '{conversation_id}' "
                    f"[status=active]"
                )
            return restored
        return False

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def find_by_id(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single conversation document by conversation_id.
        Returns documents regardless of status (including soft-deleted).
        """
        col = self._collection()
        if col is not None:
            query = {"conversation_id": conversation_id}
            if user_id and not is_admin:
                query["metadata.userId"] = user_id
            return await col.find_one(query, {"_id": 0})
        return None

    async def find_all(
        self,
        limit: int = 20,
        page: int = 1,
        sort_field: str = "created_at",
        sort_order: int = -1,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        """
        Retrieves paginated conversation documents from MongoDB.
        Excludes soft-deleted (status=deleted) conversations by default.
        """
        col = self._collection()
        if col is not None:
            # Exclude soft-deleted conversations from normal listing
            base_query = {"status": {"$ne": CONVERSATION_STATUS_DELETED}}
            if user_id and not is_admin:
                base_query["metadata.userId"] = user_id
            skip        = (page - 1) * limit
            total       = await col.count_documents(base_query)
            cursor      = (
                col.find(base_query, {"_id": 0, "messages": 0})
                   .sort(sort_field, sort_order)
                   .skip(skip)
                   .limit(limit)
            )
            docs        = await cursor.to_list(length=limit)
            total_pages = max(1, -(-total // limit))
            return {
                "documents":   docs,
                "total_count": total,
                "page":        page,
                "limit":       limit,
                "total_pages": total_pages
            }
        return {
            "documents": [], "total_count": 0,
            "page": page, "limit": limit, "total_pages": 0
        }

    async def search(
        self,
        conversation_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
        sort_field: str = "created_at",
        sort_order: int = -1,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        """
        Searches conversations with optional filters.
        Excludes soft-deleted conversations unless status='deleted' is explicitly requested.

        Args:
            conversation_id: Partial case-insensitive match.
            status:          active | archived | deleted (explicit).
            date_from:       ISO 8601 lower bound on created_at.
            date_to:         ISO 8601 upper bound on created_at.
        """
        col = self._collection()
        if col is None:
            return {
                "documents": [], "total_count": 0,
                "page": page, "limit": limit, "total_pages": 0
            }

        # Exclude soft-deleted unless caller explicitly requests status=deleted
        query: Dict[str, Any] = {}
        if user_id and not is_admin:
            query["metadata.userId"] = user_id
        if status:
            query["status"] = status.lower()
        else:
            query["status"] = {"$ne": CONVERSATION_STATUS_DELETED}

        if conversation_id:
            query["conversation_id"] = {
                "$regex":   conversation_id,
                "$options": "i"
            }

        if date_from or date_to:
            date_filter: Dict[str, str] = {}
            if date_from:
                date_filter["$gte"] = date_from
            if date_to:
                date_filter["$lte"] = date_to
            query["created_at"] = date_filter

        skip        = (page - 1) * limit
        total       = await col.count_documents(query)
        cursor      = (
            col.find(query, {"_id": 0, "messages": 0})
               .sort(sort_field, sort_order)
               .skip(skip)
               .limit(limit)
        )
        docs        = await cursor.to_list(length=limit)
        total_pages = max(1, -(-total // limit)) if total else 0

        logger.info(
            f"[ConversationRepo] Search | "
            f"convId:{conversation_id}, status:{status}, "
            f"date:{date_from}→{date_to} | "
            f"results={total} | page={page}/{total_pages}"
        )
        return {
            "documents":   docs,
            "total_count": total,
            "page":        page,
            "limit":       limit,
            "total_pages": total_pages
        }

    # ------------------------------------------------------------------
    # Counts
    # ------------------------------------------------------------------

    async def count(self, include_deleted: bool = False) -> int:
        """Returns total conversation count, excluding soft-deleted by default."""
        col = self._collection()
        if col is not None:
            query = {} if include_deleted else {"status": {"$ne": CONVERSATION_STATUS_DELETED}}
            return await col.count_documents(query)
        return 0

    async def count_by_status(self) -> Dict[str, int]:
        """Returns a breakdown of conversation counts by status."""
        col = self._collection()
        if col is not None:
            pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
            result = await col.aggregate(pipeline).to_list(length=10)
            return {row["_id"]: row["count"] for row in result}
        return {"active": 0, "archived": 0, "deleted": 0}

    async def exists(self, conversation_id: str, user_id: Optional[str] = None, is_admin: bool = False) -> bool:
        """
        Returns True if the conversation exists and is NOT soft-deleted.
        """
        col = self._collection()
        if col is not None:
            query = {
                "conversation_id": conversation_id,
                "status":          {"$ne": CONVERSATION_STATUS_DELETED}
            }
            if user_id and not is_admin:
                query["metadata.userId"] = user_id
            n = await col.count_documents(query)
            return n > 0
        return False

    async def exists_any(self, conversation_id: str, user_id: Optional[str] = None, is_admin: bool = False) -> bool:
        """
        Returns True if the conversation exists regardless of status
        (including soft-deleted).
        """
        col = self._collection()
        if col is not None:
            query = {"conversation_id": conversation_id}
            if user_id and not is_admin:
                query["metadata.userId"] = user_id
            n = await col.count_documents(query)
            return n > 0
        return False


conversation_repository = ConversationRepository()
