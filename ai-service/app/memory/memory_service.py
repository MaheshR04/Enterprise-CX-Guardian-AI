from typing import List, Optional, Dict, Any
from app.repositories.interfaces import (
    IConversationRepository,
    IMessageRepository,
    IPromptRepository,
    IUsageRepository,
)
from app.repositories.factory import repository_factory
from app.core.config import settings
from app.core.logger import logger
from app.utils.exceptions import DuplicateConversationIdException


class MemoryService:
    """
    Memory & Context Window Service for Enterprise CX Guardian AI.

    Replaces in-memory dict storage with MongoDB-backed repository layer.
    All reads/writes are permanently persisted via ConversationRepository
    and MessageRepository. Business logic only — no raw MongoDB queries here.

    Exposes a clean API consumed by AIServiceManager and conversation routers.
    """

    def __init__(
        self,
        conv_repo: IConversationRepository = None,
        msg_repo:  IMessageRepository = None,
        prompt_repo: IPromptRepository = None,
        usage_repo: IUsageRepository = None,
        max_history: int = None
    ):
        # Resolve from RepositoryFactory by default — interface-typed,
        # so any backend (MongoDB, Redis, Postgres) can be injected.
        self._conv_repo: IConversationRepository = (
            conv_repo or repository_factory.get_conversation_repo()
        )
        self._msg_repo: IMessageRepository = (
            msg_repo or repository_factory.get_message_repo()
        )
        self._prompt_repo: IPromptRepository = (
            prompt_repo or repository_factory.get_prompt_repo()
        )
        self._usage_repo: IUsageRepository = (
            usage_repo or repository_factory.get_usage_repo()
        )
        self._max_history: int = (
            max_history if max_history is not None else settings.MAX_HISTORY
        )

    # ==============================================================
    # 1. createConversation()
    # ==============================================================
    async def createConversation(
        self,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates and permanently stores a new conversation session in MongoDB.
        Returns the created conversation document.
        """
        import uuid
        cid = conversation_id or f"conv_{uuid.uuid4()}"

        if await self._conv_repo.exists_any(cid):
            raise DuplicateConversationIdException(cid)

        doc = await self._conv_repo.insert_one(
            conversation_id=cid,
            metadata=metadata,
            user_id=user_id
        )
        logger.info(f"[MemoryService] Created conversation '{cid}'")
        return doc

    # snake_case alias
    async def create_conversation(
        self,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.createConversation(conversation_id=conversation_id, metadata=metadata, user_id=user_id)

    # ==============================================================
    # 2. saveMessage()
    # ==============================================================
    async def saveMessage(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Persists a new message (user | assistant | system) to MongoDB
        and updates the parent conversation's updatedAt timestamp.
        Returns the persisted message document.
        """
        msg = await self._msg_repo.insert_one(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata=metadata
        )
        await self._conv_repo.update_timestamp(conversation_id)
        logger.info(
            f"[MemoryService] Saved '{role}' message '{msg['message_id']}' "
            f"to conversation '{conversation_id}'"
        )
        return msg

    # snake_case alias
    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        return await self.saveMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata=metadata
        )

    # ==============================================================
    # 3. loadConversation()
    # ==============================================================
    async def loadConversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves a conversation document from MongoDB with messages and telemetry.
        Returns None if the conversation does not exist.
        """
        conv = await self._conv_repo.find_by_id(conversation_id, user_id=user_id, is_admin=is_admin)
        if not conv:
            logger.info(f"[MemoryService] Conversation '{conversation_id}' not found in MongoDB")
            return None

        messages = await self._msg_repo.find_by_conversation_id(conversation_id)
        prompt_stats = await self._prompt_repo.get_prompt_stats_by_conversation(conversation_id)
        usage_summary = await self._usage_repo.sum_tokens_by_conversation_id(conversation_id)
        latest_prompt = await self._prompt_repo.find_latest_by_conversation_id(conversation_id)
        latest_usage = await self._usage_repo.find_latest_by_conversation_id(conversation_id)

        conv["messages"] = messages
        conv["message_count"] = len(messages)
        conv["prompt_stats"] = prompt_stats
        conv["usage_summary"] = usage_summary
        conv["latest_prompt"] = latest_prompt
        conv["latest_usage"] = latest_usage
        return conv

    # snake_case alias
    async def load_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Optional[Dict[str, Any]]:
        return await self.loadConversation(conversation_id, user_id=user_id, is_admin=is_admin)

    # ==============================================================
    # 4. deleteConversation()  — SOFT DELETE
    # ==============================================================
    async def deleteConversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        """
        Soft-deletes a conversation by setting status=DELETED.
        The MongoDB document is NEVER permanently removed.
        Soft-deleted conversations are excluded from all list/search queries.
        Returns True if successfully soft-deleted, False if not found.
        """
        if not is_admin and user_id:
            existing = await self._conv_repo.find_by_id(conversation_id, user_id=user_id, is_admin=False)
            if not existing:
                return False
        deleted = await self._conv_repo.soft_delete(conversation_id)
        if deleted:
            logger.info(
                f"[MemoryService] Soft-deleted conversation '{conversation_id}' "
                f"[status=deleted]"
            )
        return deleted

    # snake_case alias
    async def delete_conversation(self, conversation_id: str) -> bool:
        return await self.deleteConversation(conversation_id)

    # ==============================================================
    # archiveConversation()
    # ==============================================================
    async def archiveConversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        """
        Archives a conversation by setting status=ARCHIVED.
        Archived conversations remain visible in list/search results.
        Returns True if successfully archived, False if not found.
        """
        if not is_admin and user_id:
            existing = await self._conv_repo.find_by_id(conversation_id, user_id=user_id, is_admin=False)
            if not existing:
                return False
        archived = await self._conv_repo.archive(conversation_id)
        if archived:
            logger.info(
                f"[MemoryService] Archived conversation '{conversation_id}' "
                f"[status=archived]"
            )
        return archived

    # snake_case alias
    async def archive_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        return await self.archiveConversation(conversation_id, user_id=user_id, is_admin=is_admin)

    # ==============================================================
    # restoreConversation()
    # ==============================================================
    async def restoreConversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        """
        Restores a DELETED or ARCHIVED conversation back to ACTIVE status.
        Returns True if successfully restored, False if not found.
        """
        if not is_admin and user_id:
            existing = await self._conv_repo.find_by_id(conversation_id, user_id=user_id, is_admin=False)
            if not existing:
                return False
        restored = await self._conv_repo.restore(conversation_id)
        if restored:
            logger.info(
                f"[MemoryService] Restored conversation '{conversation_id}' "
                f"[status=active]"
            )
        return restored

    # snake_case alias
    async def restore_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        return await self.restoreConversation(conversation_id, user_id=user_id, is_admin=is_admin)

    # ==============================================================
    # 5. listConversations()
    # ==============================================================
    async def listConversations(
        self,
        limit: int = 20,
        page: int = 1,
        sort: str = "desc",
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        """
        Returns a paginated list of conversation documents from MongoDB,
        enriched with message_count for each session.

        Args:
            limit: Documents per page (default 20).
            page:  1-indexed page number (default 1).
            sort:  'desc' for newest first, 'asc' for oldest first.
        """
        sort_order = -1 if sort.lower() == "desc" else 1
        result = await self._conv_repo.find_all(
            limit=limit,
            page=page,
            sort_field="created_at",
            sort_order=sort_order,
            user_id=user_id,
            is_admin=is_admin
        )

        # Enrich each document with live message count
        enriched = []
        for conv in result["documents"]:
            cid       = conv.get("conversation_id")
            msg_count = await self._msg_repo.count_by_conversation_id(cid)
            enriched.append({
                "conversation_id": cid,
                "created_at":      conv.get("created_at"),
                "updated_at":      conv.get("updated_at"),
                "status":          conv.get("status", "active"),
                "message_count":   msg_count,
                "metadata":        conv.get("metadata", {})
            })

        logger.info(
            f"[MemoryService] Listed {len(enriched)} conversations "
            f"(page={page}, limit={limit}, sort={sort})"
        )
        return {
            "conversations": enriched,
            "total_count":   result["total_count"],
            "page":          result["page"],
            "limit":         result["limit"],
            "total_pages":   result["total_pages"]
        }

    # snake_case alias
    async def list_conversations(
        self,
        limit: int = 20,
        page: int = 1,
        sort: str = "desc",
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        return await self.listConversations(limit=limit, page=page, sort=sort, user_id=user_id, is_admin=is_admin)

    # ==============================================================
    # searchConversations()
    # ==============================================================
    async def searchConversations(
        self,
        conversation_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
        sort: str = "desc",
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        """
        Searches conversations in MongoDB with optional filters:
        - conversationId: partial case-insensitive match
        - status:         exact match (active | closed | archived)
        - date_from:      ISO 8601 lower bound on createdAt
        - date_to:        ISO 8601 upper bound on createdAt

        Results are paginated and enriched with message_count.
        """
        sort_order = -1 if sort.lower() == "desc" else 1
        result = await self._conv_repo.search(
            conversation_id=conversation_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            page=page,
            sort_field="created_at",
            sort_order=sort_order,
            user_id=user_id,
            is_admin=is_admin
        )

        # Enrich each document with live message count
        enriched = []
        for conv in result["documents"]:
            cid       = conv.get("conversation_id")
            msg_count = await self._msg_repo.count_by_conversation_id(cid)
            enriched.append({
                "conversation_id": cid,
                "created_at":      conv.get("created_at"),
                "updated_at":      conv.get("updated_at"),
                "status":          conv.get("status", "active"),
                "message_count":   msg_count,
                "metadata":        conv.get("metadata", {})
            })

        logger.info(
            f"[MemoryService] Search returned {len(enriched)} conversations "
            f"(convId={conversation_id}, status={status}, "
            f"date={date_from}→{date_to}, page={page}, limit={limit})"
        )
        return {
            "conversations": enriched,
            "total_count":   result["total_count"],
            "page":          result["page"],
            "limit":         result["limit"],
            "total_pages":   result["total_pages"]
        }

    # snake_case alias
    async def search_conversations(
        self,
        conversation_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
        sort: str = "desc",
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        return await self.searchConversations(
            conversation_id=conversation_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            page=page,
            sort=sort,
            user_id=user_id,
            is_admin=is_admin
        )

    # ==============================================================
    # 6. clearConversation()
    # ==============================================================
    async def clearConversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        """
        Clears all messages in a conversation without deleting the
        conversation document itself. Resets updatedAt timestamp.
        Returns True if messages were cleared.
        """
        if not is_admin and user_id:
            existing = await self._conv_repo.find_by_id(conversation_id, user_id=user_id, is_admin=False)
            if not existing:
                return False
        deleted_count = await self._msg_repo.delete_by_conversation_id(conversation_id)
        await self._conv_repo.update_timestamp(conversation_id)
        logger.info(
            f"[MemoryService] Cleared {deleted_count} messages from conversation '{conversation_id}'"
        )
        return deleted_count > 0

    # snake_case alias
    async def clear_conversation(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        return await self.clearConversation(conversation_id, user_id=user_id, is_admin=is_admin)

    # ==============================================================
    # Context Window Helpers (used by AIServiceManager)
    # ==============================================================
    async def getRecentMessages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the N most recent messages bounded by MAX_HISTORY
        for LLM context window injection.
        """
        n = limit if limit is not None else self._max_history
        messages = await self._msg_repo.find_recent_by_conversation_id(
            conversation_id=conversation_id,
            limit=n
        )
        logger.info(
            f"[MemoryService] Loaded {len(messages)} recent messages "
            f"for conversation '{conversation_id}' (limit: {n})"
        )
        return messages

    async def get_recent_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        return await self.getRecentMessages(conversation_id=conversation_id, limit=limit)

    async def formatHistoryForPrompt(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> str:
        """
        Retrieves recent messages and formats them as a clean
        multi-turn dialogue string for PromptBuilder injection.
        """
        messages = await self.getRecentMessages(conversation_id, limit=limit)
        if not messages:
            return ""
        lines = []
        for msg in messages:
            role_label = "Customer" if msg.get("role") == "user" else "AI"
            lines.append(f"{role_label}: {msg.get('content', '')}")
        return "\n".join(lines)

    async def format_history_for_prompt(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> str:
        return await self.formatHistoryForPrompt(conversation_id=conversation_id, limit=limit)

    async def conversationExists(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        """
        Checks whether a conversation session exists in MongoDB.
        """
        return await self._conv_repo.exists(conversation_id, user_id=user_id, is_admin=is_admin)

    async def conversation_exists(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        return await self.conversationExists(conversation_id, user_id=user_id, is_admin=is_admin)

    async def conversationExistsAny(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        """
        Checks whether a conversation exists in any lifecycle state.
        """
        return await self._conv_repo.exists_any(conversation_id, user_id=user_id, is_admin=is_admin)

    async def conversation_exists_any(
        self,
        conversation_id: str,
        user_id: Optional[str] = None,
        is_admin: bool = False
    ) -> bool:
        return await self.conversationExistsAny(conversation_id, user_id=user_id, is_admin=is_admin)


memory_service = MemoryService()
