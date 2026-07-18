import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.database.connection import db_connection
from app.core.config import settings
from app.core.logger import logger


class UsageRepository:
    """
    MongoDB CRUD Repository for AI Usage Telemetry Documents.
    Pure database operations only. No business logic.
    Collection: AI_USAGE_COLLECTION

    Automatically stores all 6 token usage metrics on every Groq completion call:
    — promptTokens, completionTokens, totalTokens, model, latencyMs, timestamp.
    """

    def _collection(self):
        return db_connection.get_collection(settings.AI_USAGE_COLLECTION)

    async def insert_one(
        self,
        conversation_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency_ms: float,
        processing_time: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Inserts a new AI usage telemetry document into MongoDB.
        Automatically captures all 6 required metrics:
        promptTokens, completionTokens, totalTokens, model, latencyMs, timestamp.
        """
        doc = {
            "usage_id":          f"usg_{uuid.uuid4()}",
            "conversation_id":   conversation_id,
            "model":             model,
            "prompt_tokens":     prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens":      total_tokens,
            "latency_ms":        latency_ms,
            "processing_time":   processing_time,
            "timestamp":         datetime.utcnow().isoformat(),
            "metadata":          metadata or {}
        }
        col = self._collection()
        if col is not None:
            await col.insert_one({**doc})
            logger.info(
                f"[UsageRepo] Stored usage '{doc['usage_id']}' | "
                f"Conv: {conversation_id} | Model: {model} | "
                f"Tokens: prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens} | "
                f"Latency: {latency_ms:.2f}ms"
            )
        return doc

    async def find_by_conversation_id(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all AI usage records for a conversation ordered by timestamp ascending.
        """
        col = self._collection()
        if col is not None:
            cursor = col.find(
                {"conversation_id": conversation_id},
                {"_id": 0}
            ).sort("timestamp", 1).limit(limit)
            return await cursor.to_list(length=limit)
        return []

    async def find_by_id(self, usage_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single usage telemetry document by usage_id.
        """
        col = self._collection()
        if col is not None:
            return await col.find_one({"usage_id": usage_id}, {"_id": 0})
        return None

    async def find_latest_by_conversation_id(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves the most recent usage record for a conversation.
        """
        col = self._collection()
        if col is not None:
            return await col.find_one(
                {"conversation_id": conversation_id},
                {"_id": 0},
                sort=[("timestamp", -1)]
            )
        return None

    async def find_by_model(
        self,
        model: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all usage records for a specific model name.
        """
        col = self._collection()
        if col is not None:
            cursor = col.find(
                {"model": model},
                {"_id": 0}
            ).sort("timestamp", -1).limit(limit)
            return await cursor.to_list(length=limit)
        return []

    async def delete_by_conversation_id(self, conversation_id: str) -> int:
        """
        Deletes all usage records belonging to a conversation.
        """
        col = self._collection()
        if col is not None:
            result = await col.delete_many({"conversation_id": conversation_id})
            logger.info(
                f"[UsageRepo] Deleted {result.deleted_count} usage records "
                f"for conversation '{conversation_id}'"
            )
            return result.deleted_count
        return 0

    async def delete_by_id(self, usage_id: str) -> bool:
        """
        Deletes a single usage record by usage_id.
        """
        col = self._collection()
        if col is not None:
            result = await col.delete_one({"usage_id": usage_id})
            return result.deleted_count > 0
        return False

    async def count_by_conversation_id(self, conversation_id: str) -> int:
        """
        Returns total usage record count for a given conversation.
        """
        col = self._collection()
        if col is not None:
            return await col.count_documents({"conversation_id": conversation_id})
        return 0

    async def sum_tokens_by_conversation_id(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Aggregates total token consumption and average latency
        across all usage records for a conversation.
        """
        col = self._collection()
        if col is not None:
            pipeline = [
                {"$match": {"conversation_id": conversation_id}},
                {"$group": {
                    "_id":                    None,
                    "total_prompt_tokens":    {"$sum": "$prompt_tokens"},
                    "total_completion_tokens":{"$sum": "$completion_tokens"},
                    "total_tokens":           {"$sum": "$total_tokens"},
                    "avg_latency_ms":         {"$avg": "$latency_ms"},
                    "call_count":             {"$sum": 1}
                }}
            ]
            result = await col.aggregate(pipeline).to_list(length=1)
            if result:
                return {
                    "total_prompt_tokens":     result[0].get("total_prompt_tokens", 0),
                    "total_completion_tokens": result[0].get("total_completion_tokens", 0),
                    "total_tokens":            result[0].get("total_tokens", 0),
                    "avg_latency_ms":          round(result[0].get("avg_latency_ms", 0.0), 2),
                    "call_count":              result[0].get("call_count", 0)
                }
        return {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "avg_latency_ms": 0.0,
            "call_count": 0
        }


usage_repository = UsageRepository()
