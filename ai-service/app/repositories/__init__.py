# Interfaces (abstract contracts)
from app.repositories.interfaces import (
    IConversationRepository,
    IMessageRepository,
    IPromptRepository,
    IUsageRepository
)

# Factory (backend resolution)
from app.repositories.factory import repository_factory, RepositoryFactory

# MongoDB implementations
from app.repositories.conversation_repository import conversation_repository, ConversationRepository
from app.repositories.message_repository import message_repository, MessageRepository
from app.repositories.prompt_repository import prompt_repository, PromptRepository
from app.repositories.usage_repository import usage_repository, UsageRepository

__all__ = [
    # Interfaces
    "IConversationRepository",
    "IMessageRepository",
    "IPromptRepository",
    "IUsageRepository",
    # Factory
    "repository_factory",
    "RepositoryFactory",
    # Implementations
    "conversation_repository",
    "ConversationRepository",
    "message_repository",
    "MessageRepository",
    "prompt_repository",
    "PromptRepository",
    "usage_repository",
    "UsageRepository"
]
