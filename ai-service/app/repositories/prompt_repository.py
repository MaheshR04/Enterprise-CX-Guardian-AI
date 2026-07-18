import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.database.connection import db_connection
from app.core.config import settings
from app.core.logger import logger


class PromptRepository:
    """
    MongoDB CRUD Repository for Prompt Log Documents.
    Pure database operations only. No business logic.
    Collection: PROMPT_LOG_COLLECTION

    Saves every generated prompt payload for:
    - Debugging (inspect exact LLM inputs on every turn)
    - Analytics  (prompt size trends, model behaviour patterns)
    - Future prompt optimisation (replay, A/B testing, fine-tuning datasets)
    """

    def _collection(self):
        return db_connection.get_collection(settings.PROMPT_LOG_COLLECTION)

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    async def insert_one(
        self,
        conversation_id: str,
        system_prompt: str,
        user_prompt: str,
        final_prompt: str,
        model: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Inserts a new prompt log document into MongoDB.
        Called automatically after every Groq completion request.
        """
        doc = {
            "prompt_id":       f"prompt_{uuid.uuid4()}",
            "conversation_id": conversation_id,
            "system_prompt":   system_prompt,
            "user_prompt":     user_prompt,
            "final_prompt":    final_prompt,
            "prompt_size":     len(final_prompt),
            "model":           model,
            "created_at":      datetime.utcnow().isoformat(),
            "metadata":        metadata or {}
        }
        col = self._collection()
        if col is not None:
            await col.insert_one({**doc})
            logger.info(
                f"[PromptRepo] Saved prompt log '{doc['prompt_id']}' | "
                f"Conv: {conversation_id} | Model: {model} | "
                f"Size: {doc['prompt_size']} chars"
            )
        return doc

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def find_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single prompt log document by prompt_id.
        """
        col = self._collection()
        if col is not None:
            return await col.find_one({"prompt_id": prompt_id}, {"_id": 0})
        return None

    async def find_by_conversation_id(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all prompt logs for a conversation ordered by createdAt ascending.
        Useful for full conversation prompt audit trail.
        """
        col = self._collection()
        if col is not None:
            cursor = col.find(
                {"conversation_id": conversation_id},
                {"_id": 0}
            ).sort("created_at", 1).limit(limit)
            return await cursor.to_list(length=limit)
        return []

    async def find_latest_by_conversation_id(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves the most recently generated prompt log for a conversation.
        Useful for debugging the last LLM input.
        """
        col = self._collection()
        if col is not None:
            return await col.find_one(
                {"conversation_id": conversation_id},
                {"_id": 0},
                sort=[("created_at", -1)]
            )
        return None

    async def find_by_model(
        self,
        model: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all prompt logs for a given model name.
        Useful for model-level analytics and prompt pattern analysis.
        """
        col = self._collection()
        if col is not None:
            cursor = col.find(
                {"model": model},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit)
            return await cursor.to_list(length=limit)
        return []

    async def find_large_prompts(
        self,
        min_size: int = 1000,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieves prompt logs exceeding a minimum character size threshold.
        Useful for identifying context overflow risks.
        """
        col = self._collection()
        if col is not None:
            cursor = col.find(
                {"prompt_size": {"$gte": min_size}},
                {"_id": 0}
            ).sort("prompt_size", -1).limit(limit)
            return await cursor.to_list(length=limit)
        return []

    # ------------------------------------------------------------------
    # Aggregation / Analytics
    # ------------------------------------------------------------------

    async def get_prompt_stats_by_conversation(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Aggregates prompt analytics for a conversation:
        total prompts, average prompt size, min/max prompt size.
        """
        col = self._collection()
        if col is not None:
            pipeline = [
                {"$match": {"conversation_id": conversation_id}},
                {"$group": {
                    "_id":              None,
                    "total_prompts":    {"$sum": 1},
                    "avg_prompt_size":  {"$avg": "$prompt_size"},
                    "max_prompt_size":  {"$max": "$prompt_size"},
                    "min_prompt_size":  {"$min": "$prompt_size"},
                    "total_chars":      {"$sum": "$prompt_size"}
                }}
            ]
            result = await col.aggregate(pipeline).to_list(length=1)
            if result:
                return {
                    "total_prompts":   result[0].get("total_prompts", 0),
                    "avg_prompt_size": round(result[0].get("avg_prompt_size", 0.0), 1),
                    "max_prompt_size": result[0].get("max_prompt_size", 0),
                    "min_prompt_size": result[0].get("min_prompt_size", 0),
                    "total_chars":     result[0].get("total_chars", 0)
                }
        return {
            "total_prompts": 0, "avg_prompt_size": 0.0,
            "max_prompt_size": 0, "min_prompt_size": 0, "total_chars": 0
        }

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete_by_conversation_id(self, conversation_id: str) -> int:
        """
        Deletes all prompt log documents for a conversation.
        """
        col = self._collection()
        if col is not None:
            result = await col.delete_many({"conversation_id": conversation_id})
            logger.info(
                f"[PromptRepo] Deleted {result.deleted_count} prompt logs "
                f"for conversation '{conversation_id}'"
            )
            return result.deleted_count
        return 0

    async def delete_by_id(self, prompt_id: str) -> bool:
        """
        Deletes a single prompt log document by prompt_id.
        """
        col = self._collection()
        if col is not None:
            result = await col.delete_one({"prompt_id": prompt_id})
            return result.deleted_count > 0
        return False

    async def count_by_conversation_id(self, conversation_id: str) -> int:
        """
        Returns total prompt log count for a given conversation.
        """
        col = self._collection()
        if col is not None:
            return await col.count_documents({"conversation_id": conversation_id})
        return 0


prompt_repository = PromptRepository()
