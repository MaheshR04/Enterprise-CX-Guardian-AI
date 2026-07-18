import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.database.connection import db_connection
from app.core.config import settings
from app.core.logger import logger


class MessageRepository:
    """
    MongoDB CRUD Repository for Message Documents.
    Pure database operations only. No business logic.
    Collection: MESSAGE_COLLECTION
    """

    def _collection(self):
        return db_connection.get_collection(settings.MESSAGE_COLLECTION)

    async def insert_one(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Inserts a new message document into MongoDB.
        """
        doc = {
            "message_id": f"msg_{uuid.uuid4()}",
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "tokens": {},
            "metadata": metadata or {}
        }
        col = self._collection()
        if col is not None:
            await col.insert_one({**doc})
            logger.info(f"[MessageRepo] Inserted '{role}' message '{doc['message_id']}' for conversation '{conversation_id}'")
        return doc

    async def find_by_conversation_id(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all messages for a conversation, ordered by timestamp ascending.
        """
        col = self._collection()
        if col is not None:
            query = {"conversation_id": conversation_id}
            cursor = col.find(query, {"_id": 0}).sort("timestamp", 1)
            if limit:
                cursor = cursor.limit(limit)
            return await cursor.to_list(length=limit or 1000)
        return []

    async def find_recent_by_conversation_id(
        self,
        conversation_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the N most recent messages for a conversation ordered by timestamp ascending.
        """
        col = self._collection()
        if col is not None:
            # Sort descending to get latest, then reverse for chronological order
            cursor = col.find(
                {"conversation_id": conversation_id},
                {"_id": 0}
            ).sort("timestamp", -1).limit(limit)
            docs = await cursor.to_list(length=limit)
            return list(reversed(docs))
        return []

    async def find_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single message document by message_id.
        """
        col = self._collection()
        if col is not None:
            return await col.find_one({"message_id": message_id}, {"_id": 0})
        return None

    async def delete_by_conversation_id(self, conversation_id: str) -> int:
        """
        Deletes all message documents belonging to a conversation.
        """
        col = self._collection()
        if col is not None:
            result = await col.delete_many({"conversation_id": conversation_id})
            logger.info(f"[MessageRepo] Deleted {result.deleted_count} messages for conversation '{conversation_id}'")
            return result.deleted_count
        return 0

    async def delete_by_id(self, message_id: str) -> bool:
        """
        Deletes a single message document by message_id.
        """
        col = self._collection()
        if col is not None:
            result = await col.delete_one({"message_id": message_id})
            return result.deleted_count > 0
        return False

    async def count_by_conversation_id(self, conversation_id: str) -> int:
        """
        Returns the total message count for a given conversation.
        """
        col = self._collection()
        if col is not None:
            return await col.count_documents({"conversation_id": conversation_id})
        return 0


message_repository = MessageRepository()
