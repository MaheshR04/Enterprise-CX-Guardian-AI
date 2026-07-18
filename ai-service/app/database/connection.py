"""
MongoDB Atlas Async Connection Manager for Enterprise CX Guardian AI.
Instruments all 4 logging categories:
  1. Database connections  — connect, ping, disconnect events
  2. CRUD operations       — collection access
  3. Errors               — connection failures, health check errors
  4. Latency              — ping round-trip, connection setup time
"""

import time
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.core.logger import (
    logger,
    log_db_connecting,
    log_db_connected,
    log_db_disconnected,
    log_db_error,
    log_db_fallback,
    log_db_health,
    log_crud_find
)

# Mask credentials from URI for safe logging
def _mask_uri(uri: str) -> str:
    """Returns a credential-masked version of the MongoDB URI for logs."""
    try:
        if "@" in uri:
            prefix = uri[:uri.index("//") + 2]
            suffix = uri[uri.index("@"):]
            return f"{prefix}****:****{suffix}"
        return uri
    except Exception:
        return "mongodb://****"


class DatabaseConnection:
    """
    MongoDB Atlas Async Connection Client Manager.

    Responsibilities:
    - Connect to MongoDB Atlas with Motor async driver
    - Manage connection pooling (minPoolSize / maxPoolSize)
    - Log all connection lifecycle events with latency
    - Expose health check with ping latency
    - Gracefully shut down on application exit
    - Operate in resilient fallback mode if MongoDB is unreachable
    """

    client: Optional[AsyncIOMotorClient] = None
    db = None
    _connected: bool = False
    _db_name: str = ""

    # ──────────────────────────────────────────────────────────────
    # 1. Connect
    # ──────────────────────────────────────────────────────────────

    @classmethod
    async def connect_to_mongo(cls) -> None:
        """
        Establishes an async connection to MongoDB Atlas.
        Logs connection attempt, success with latency, or fallback on failure.
        """
        cls._db_name = settings.DB_NAME
        uri_masked   = _mask_uri(settings.MONGODB_URI)

        log_db_connecting(uri_masked=uri_masked, db_name=cls._db_name)

        connect_start = time.perf_counter()
        try:
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                maxPoolSize=100,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            cls.db = cls.client[cls._db_name]

            # Verify connection with a ping and measure round-trip latency
            ping_start = time.perf_counter()
            await cls.client.admin.command("ping")
            ping_latency_ms = (time.perf_counter() - ping_start) * 1000

            cls._connected = True
            log_db_connected(
                db_name=cls._db_name,
                pool_min=10,
                pool_max=100,
                latency_ms=ping_latency_ms
            )
            logger.info(
                f"[DB Connect] Collections registered: "
                f"conversations | messages | prompt_logs | ai_usage | users"
            )
            await cls.ensure_indexes()

        except Exception as err:
            elapsed_ms = (time.perf_counter() - connect_start) * 1000
            log_db_error(operation="connect", error=err)
            log_db_fallback(reason=str(err))
            logger.warning(
                f"[DB Connect] Failed after {elapsed_ms:.2f}ms — "
                f"microservice will operate in resilient fallback mode"
            )
            cls.db         = None
            cls._connected = False

    # ──────────────────────────────────────────────────────────────
    # 2. Disconnect
    # ──────────────────────────────────────────────────────────────

    @classmethod
    async def close_connection(cls) -> None:
        """
        Closes the Motor MongoDB connection pool gracefully on shutdown.
        """
        if cls.client:
            cls.client.close()
            cls._connected = False
            log_db_disconnected(db_name=cls._db_name)
        else:
            logger.debug("[DB Disconnect] No active connection to close")

    # ──────────────────────────────────────────────────────────────
    # 3. Health Check
    # ──────────────────────────────────────────────────────────────

    @classmethod
    async def check_health(cls) -> Dict[str, Any]:
        """
        Pings MongoDB and returns a health status dict with latency.
        Logs the result using the structured log_db_health helper.
        """
        if not cls.client:
            result = {
                "status":   "unhealthy",
                "database": cls._db_name or settings.DB_NAME,
                "error":    "MongoDB client not initialized — operating in fallback mode"
            }
            log_db_health(
                db_name=result["database"],
                status="unhealthy",
                error=result["error"]
            )
            return result

        try:
            start = time.perf_counter()
            await cls.client.admin.command("ping")
            ping_ms = (time.perf_counter() - start) * 1000

            result = {
                "status":        "healthy",
                "database":      cls._db_name,
                "ping_latency":  f"{ping_ms:.2f}ms"
            }
            log_db_health(
                db_name=cls._db_name,
                status="healthy",
                ping_latency_ms=ping_ms
            )
            return result

        except Exception as err:
            log_db_error(operation="health_check", error=err)
            return {
                "status":   "unhealthy",
                "database": cls._db_name,
                "error":    str(err)
            }

    # ──────────────────────────────────────────────────────────────
    # 4. Collection Access (with CRUD logging)
    # ──────────────────────────────────────────────────────────────

    @classmethod
    def get_collection(cls, collection_name: str):
        """
        Retrieves a MongoDB collection instance.
        Logs collection access and warns when operating in fallback mode.
        """
        if cls.db is not None:
            logger.debug(f"[DB Collection] Accessing collection '{collection_name}'")
            return cls.db[collection_name]

        logger.warning(
            f"[DB Collection] Collection '{collection_name}' requested but "
            f"MongoDB is unavailable — returning None (fallback mode)"
        )
        return None

    @classmethod
    async def ensure_indexes(cls) -> None:
        """
        Creates MongoDB indexes used by CRUD, pagination, search, prompt audit,
        and token usage analytics. Safe to call repeatedly at startup.
        """
        if cls.db is None:
            logger.warning("[DB Indexes] Skipped index creation because MongoDB is unavailable")
            return

        index_specs = {
            settings.CONVERSATION_COLLECTION: [
                ([("conversation_id", 1)], {"unique": True, "name": "uq_conversation_id"}),
                ([("status", 1), ("created_at", -1)], {"name": "idx_status_created_at"}),
                ([("created_at", -1)], {"name": "idx_created_at_desc"}),
                ([("updated_at", -1)], {"name": "idx_updated_at_desc"}),
            ],
            settings.MESSAGE_COLLECTION: [
                ([("message_id", 1)], {"unique": True, "name": "uq_message_id"}),
                ([("conversation_id", 1), ("timestamp", 1)], {"name": "idx_conversation_timestamp"}),
            ],
            settings.PROMPT_LOG_COLLECTION: [
                ([("prompt_id", 1)], {"unique": True, "name": "uq_prompt_id"}),
                ([("conversation_id", 1), ("created_at", -1)], {"name": "idx_prompt_conversation_created"}),
                ([("model", 1), ("created_at", -1)], {"name": "idx_prompt_model_created"}),
            ],
            settings.AI_USAGE_COLLECTION: [
                ([("usage_id", 1)], {"unique": True, "name": "uq_usage_id"}),
                ([("conversation_id", 1), ("timestamp", -1)], {"name": "idx_usage_conversation_timestamp"}),
                ([("model", 1), ("timestamp", -1)], {"name": "idx_usage_model_timestamp"}),
            ],
            settings.USER_COLLECTION: [
                ([("userId", 1)], {"unique": True, "name": "uq_user_id"}),
                ([("email", 1)], {"unique": True, "name": "uq_user_email"}),
            ],
            settings.REFRESH_TOKEN_COLLECTION: [
                ([("tokenHash", 1)], {"unique": True, "name": "uq_refresh_token_hash"}),
                ([("userId", 1), ("revoked", 1)], {"name": "idx_refresh_token_user_revoked"}),
            ],
        }

        for collection_name, specs in index_specs.items():
            collection = cls.db[collection_name]
            for keys, options in specs:
                await collection.create_index(keys, **options)

        logger.info("[DB Indexes] MongoDB indexes verified for conversation storage")

    # ──────────────────────────────────────────────────────────────
    # Properties
    # ──────────────────────────────────────────────────────────────

    @classmethod
    def is_connected(cls) -> bool:
        """Returns True if MongoDB is connected and available."""
        return cls._connected and cls.db is not None


db_connection = DatabaseConnection()
