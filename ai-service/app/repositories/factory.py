"""
Repository Factory for Enterprise CX Guardian AI.

Single registration point for all storage backend implementations.
To swap MongoDB for Redis, PostgreSQL, or Azure Cosmos DB:

  1. Implement the relevant interface from app/repositories/interfaces.py
  2. Import your new class here
  3. Set the backend name in settings (STORAGE_BACKEND)
  4. Zero changes required in controllers, services, or routers.

Current backends:
  - "mongodb"  → Motor async MongoDB (default, production-ready)
  - "memory"   → In-memory dict (testing / CI only)
"""

from typing import Literal
from app.core.config import settings
from app.core.logger import logger
from app.repositories.interfaces import (
    IConversationRepository,
    IMessageRepository,
    IPromptRepository,
    IUsageRepository
)

# ── MongoDB (default) ──────────────────────────────────────────────
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.prompt_repository import PromptRepository
from app.repositories.usage_repository import UsageRepository


# ══════════════════════════════════════════════════════════════════
# Backend Registry
# To add a new backend: add an elif block below and import your class.
# ══════════════════════════════════════════════════════════════════

StorageBackend = Literal["mongodb", "memory"]


class RepositoryFactory:
    """
    Factory that resolves and returns the correct repository
    implementation based on the configured STORAGE_BACKEND setting.

    All returned objects satisfy the abstract interface contracts,
    meaning callers (services, managers) are completely decoupled
    from the concrete storage technology.
    """

    _backend: str = None

    # Singleton instances — resolved once at startup
    _conversation_repo: IConversationRepository = None
    _message_repo:      IMessageRepository      = None
    _prompt_repo:       IPromptRepository        = None
    _usage_repo:        IUsageRepository         = None

    @classmethod
    def _resolve_backend(cls) -> str:
        backend = getattr(settings, "STORAGE_BACKEND", "mongodb").lower()
        logger.info(f"[RepositoryFactory] Storage backend resolved: '{backend}'")
        return backend

    @classmethod
    def _build_mongodb(cls) -> None:
        """Instantiates all MongoDB-backed repository implementations."""
        cls._conversation_repo = ConversationRepository()
        cls._message_repo      = MessageRepository()
        cls._prompt_repo       = PromptRepository()
        cls._usage_repo        = UsageRepository()
        logger.info(
            "[RepositoryFactory] MongoDB repositories registered: "
            "ConversationRepository | MessageRepository | "
            "PromptRepository | UsageRepository"
        )

    @classmethod
    def _build_memory(cls) -> None:
        """
        Placeholder for in-memory implementations (unit testing / CI).
        Replace with real InMemoryConversationRepository etc. when needed.
        """
        # Future:
        # from app.repositories.memory.conversation_repository import InMemoryConversationRepository
        # cls._conversation_repo = InMemoryConversationRepository()
        logger.warning(
            "[RepositoryFactory] 'memory' backend selected — "
            "falling back to MongoDB implementations for now."
        )
        cls._build_mongodb()

    # ── Future backends (uncomment when implemented) ───────────────
    # @classmethod
    # def _build_redis(cls) -> None:
    #     from app.repositories.redis.conversation_repository import RedisConversationRepository
    #     cls._conversation_repo = RedisConversationRepository()
    #     ...

    # @classmethod
    # def _build_postgres(cls) -> None:
    #     from app.repositories.postgres.conversation_repository import PostgresConversationRepository
    #     cls._conversation_repo = PostgresConversationRepository()
    #     ...

    # @classmethod
    # def _build_cosmos(cls) -> None:
    #     from app.repositories.cosmos.conversation_repository import CosmosConversationRepository
    #     cls._conversation_repo = CosmosConversationRepository()
    #     ...

    @classmethod
    def initialize(cls) -> None:
        """
        Resolves and initializes all repository singletons.
        Called once at application startup (lifespan).
        """
        cls._backend = cls._resolve_backend()

        if cls._backend == "mongodb":
            cls._build_mongodb()
        elif cls._backend == "memory":
            cls._build_memory()
        # elif cls._backend == "redis":
        #     cls._build_redis()
        # elif cls._backend == "postgres":
        #     cls._build_postgres()
        # elif cls._backend == "cosmos":
        #     cls._build_cosmos()
        else:
            logger.warning(
                f"[RepositoryFactory] Unknown backend '{cls._backend}'. "
                "Falling back to MongoDB."
            )
            cls._build_mongodb()

    # ── Accessors ──────────────────────────────────────────────────

    @classmethod
    def get_conversation_repo(cls) -> IConversationRepository:
        if cls._conversation_repo is None:
            cls.initialize()
        return cls._conversation_repo

    @classmethod
    def get_message_repo(cls) -> IMessageRepository:
        if cls._message_repo is None:
            cls.initialize()
        return cls._message_repo

    @classmethod
    def get_prompt_repo(cls) -> IPromptRepository:
        if cls._prompt_repo is None:
            cls.initialize()
        return cls._prompt_repo

    @classmethod
    def get_usage_repo(cls) -> IUsageRepository:
        if cls._usage_repo is None:
            cls.initialize()
        return cls._usage_repo

    @classmethod
    def get_active_backend(cls) -> str:
        return cls._backend or "uninitialized"


# ── Global factory singleton ───────────────────────────────────────
repository_factory = RepositoryFactory()
