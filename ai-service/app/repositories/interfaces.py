"""
Abstract Repository Interfaces for Enterprise CX Guardian AI.

These ABCs define the storage contract that all repository
implementations must satisfy. Services and controllers depend
ONLY on these interfaces — never on concrete implementations.

To swap MongoDB for Redis, PostgreSQL, or Azure Cosmos DB:
  1. Create a new class implementing the relevant interface.
  2. Register it in RepositoryFactory (app/repositories/factory.py).
  3. Zero changes required in controllers, services, or routers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class IConversationRepository(ABC):
    """
    Abstract interface for Conversation document storage.
    Any storage backend must implement all methods below.
    """

    @abstractmethod
    async def insert_one(
        self,
        conversation_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new conversation record."""
        ...

    @abstractmethod
    async def find_by_id(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a conversation by its unique ID."""
        ...

    @abstractmethod
    async def find_all(
        self,
        limit: int,
        page: int,
        sort_field: str,
        sort_order: int
    ) -> Dict[str, Any]:
        """Return a paginated list of conversations (excluding deleted)."""
        ...

    @abstractmethod
    async def search(
        self,
        conversation_id: Optional[str],
        status: Optional[str],
        date_from: Optional[str],
        date_to: Optional[str],
        limit: int,
        page: int,
        sort_field: str,
        sort_order: int
    ) -> Dict[str, Any]:
        """Search conversations by ID, status, and date range."""
        ...

    @abstractmethod
    async def update_timestamp(self, conversation_id: str) -> bool:
        """Update the updatedAt timestamp."""
        ...

    @abstractmethod
    async def update_status(self, conversation_id: str, status: str) -> bool:
        """Update the status field."""
        ...

    @abstractmethod
    async def soft_delete(self, conversation_id: str) -> bool:
        """Mark a conversation as DELETED without removing the record."""
        ...

    @abstractmethod
    async def archive(self, conversation_id: str) -> bool:
        """Mark a conversation as ARCHIVED."""
        ...

    @abstractmethod
    async def restore(self, conversation_id: str) -> bool:
        """Restore a DELETED or ARCHIVED conversation to ACTIVE."""
        ...

    @abstractmethod
    async def count(self, include_deleted: bool = False) -> int:
        """Return the total conversation count."""
        ...

    @abstractmethod
    async def count_by_status(self) -> Dict[str, int]:
        """Return a breakdown of counts per status."""
        ...

    @abstractmethod
    async def exists(self, conversation_id: str) -> bool:
        """Return True if the conversation exists and is not deleted."""
        ...

    @abstractmethod
    async def exists_any(self, conversation_id: str) -> bool:
        """Return True if the conversation exists regardless of status."""
        ...


class IMessageRepository(ABC):
    """
    Abstract interface for Message document storage.
    """

    @abstractmethod
    async def insert_one(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Persist a new message."""
        ...

    @abstractmethod
    async def find_by_conversation_id(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Return all messages for a conversation ordered by timestamp asc."""
        ...

    @abstractmethod
    async def find_recent_by_conversation_id(
        self,
        conversation_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Return the N most recent messages for context window injection."""
        ...

    @abstractmethod
    async def find_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single message by its ID."""
        ...

    @abstractmethod
    async def delete_by_conversation_id(self, conversation_id: str) -> int:
        """Delete all messages belonging to a conversation."""
        ...

    @abstractmethod
    async def delete_by_id(self, message_id: str) -> bool:
        """Delete a single message by its ID."""
        ...

    @abstractmethod
    async def count_by_conversation_id(self, conversation_id: str) -> int:
        """Return the message count for a conversation."""
        ...


class IPromptRepository(ABC):
    """
    Abstract interface for Prompt Log document storage.
    """

    @abstractmethod
    async def insert_one(
        self,
        conversation_id: str,
        system_prompt: str,
        user_prompt: str,
        final_prompt: str,
        model: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Persist a prompt log entry."""
        ...

    @abstractmethod
    async def find_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single prompt log by its ID."""
        ...

    @abstractmethod
    async def find_by_conversation_id(
        self,
        conversation_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Return all prompt logs for a conversation."""
        ...

    @abstractmethod
    async def find_latest_by_conversation_id(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Return the most recent prompt log for a conversation."""
        ...

    @abstractmethod
    async def find_by_model(
        self,
        model: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Return all prompt logs for a specific model name."""
        ...

    @abstractmethod
    async def find_large_prompts(
        self,
        min_size: int,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Return prompts exceeding a minimum character size."""
        ...

    @abstractmethod
    async def get_prompt_stats_by_conversation(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Return aggregated prompt analytics for a conversation."""
        ...

    @abstractmethod
    async def delete_by_conversation_id(self, conversation_id: str) -> int:
        """Delete all prompt logs for a conversation."""
        ...

    @abstractmethod
    async def delete_by_id(self, prompt_id: str) -> bool:
        """Delete a single prompt log by its ID."""
        ...

    @abstractmethod
    async def count_by_conversation_id(self, conversation_id: str) -> int:
        """Return the prompt log count for a conversation."""
        ...


class IUsageRepository(ABC):
    """
    Abstract interface for AI Usage Telemetry document storage.
    """

    @abstractmethod
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
        """Persist a usage telemetry record."""
        ...

    @abstractmethod
    async def find_by_conversation_id(
        self,
        conversation_id: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Return all usage records for a conversation."""
        ...

    @abstractmethod
    async def find_by_id(self, usage_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single usage record by its ID."""
        ...

    @abstractmethod
    async def find_latest_by_conversation_id(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Return the most recent usage record for a conversation."""
        ...

    @abstractmethod
    async def find_by_model(
        self,
        model: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Return all usage records for a specific model."""
        ...

    @abstractmethod
    async def delete_by_conversation_id(self, conversation_id: str) -> int:
        """Delete all usage records for a conversation."""
        ...

    @abstractmethod
    async def delete_by_id(self, usage_id: str) -> bool:
        """Delete a single usage record by its ID."""
        ...

    @abstractmethod
    async def count_by_conversation_id(self, conversation_id: str) -> int:
        """Return the usage record count for a conversation."""
        ...

    @abstractmethod
    async def sum_tokens_by_conversation_id(
        self,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Aggregate total token consumption and average latency."""
        ...
