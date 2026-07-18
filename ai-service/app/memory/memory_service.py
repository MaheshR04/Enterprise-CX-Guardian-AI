from typing import List, Dict, Optional
from app.conversation.conversation_manager import conversation_manager, ConversationManager
from app.core.config import settings
from app.core.logger import logger

class MemoryService:
    """
    Memory & Context Window Service for Enterprise CX Guardian AI.
    Provides methods for conversation management, message appending, history retrieval, and context window sliding.
    """
    def __init__(self, conv_mgr: ConversationManager = None, max_messages: int = None):
        self.conv_mgr = conv_mgr or conversation_manager
        self.max_messages = max_messages if max_messages is not None else settings.MAX_HISTORY

    # 1. createConversation / create_conversation
    def create_conversation(self, conversation_id: Optional[str] = None, metadata: Optional[dict] = None) -> dict:
        """Creates a new conversation session."""
        return self.conv_mgr.create_conversation(conversation_id=conversation_id, metadata=metadata)

    def createConversation(self, conversation_id: Optional[str] = None, metadata: Optional[dict] = None) -> dict:
        """Alias for create_conversation."""
        return self.create_conversation(conversation_id=conversation_id, metadata=metadata)

    # 2. appendMessage / append_message / store_history
    def append_message(self, conversation_id: str, role: str, content: str, metadata: Optional[dict] = None) -> dict:
        """Appends a message entry to history."""
        return self.conv_mgr.append_message(conversation_id=conversation_id, role=role, content=content, metadata=metadata)

    def appendMessage(self, conversation_id: str, role: str, content: str, metadata: Optional[dict] = None) -> dict:
        """Alias for append_message."""
        return self.append_message(conversation_id=conversation_id, role=role, content=content, metadata=metadata)

    def store_history(self, conversation_id: str, role: str, content: str, metadata: Optional[dict] = None) -> dict:
        """Alias for append_message."""
        return self.append_message(conversation_id=conversation_id, role=role, content=content, metadata=metadata)

    # 3. getConversation / get_conversation
    def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """Retrieves a conversation by session ID."""
        return self.conv_mgr.get_conversation(conversation_id)

    def getConversation(self, conversation_id: str) -> Optional[dict]:
        """Alias for get_conversation."""
        return self.get_conversation(conversation_id)

    # 4. listConversations / list_conversations
    def list_conversations(self) -> List[dict]:
        """Lists active conversations."""
        return self.conv_mgr.list_conversations()

    def listConversations(self) -> List[dict]:
        """Alias for list_conversations."""
        return self.list_conversations()

    # 5. deleteConversation / delete_conversation
    def delete_conversation(self, conversation_id: str) -> bool:
        """Deletes a conversation by session ID."""
        return self.conv_mgr.delete_conversation(conversation_id)

    def deleteConversation(self, conversation_id: str) -> bool:
        """Alias for delete_conversation."""
        return self.delete_conversation(conversation_id)

    # 6. clearHistory / clear_history
    def clear_history(self, conversation_id: str) -> bool:
        """Clears conversation history."""
        return self.delete_conversation(conversation_id)

    def clearHistory(self, conversation_id: str) -> bool:
        """Alias for clear_history."""
        return self.clear_history(conversation_id)

    # 7. getRecentMessages / get_recent_messages / get_latest_messages
    def load_history(self, conversation_id: str) -> List[dict]:
        """Loads all raw messages for a conversation."""
        conv = self.get_conversation(conversation_id)
        if not conv:
            return []
        return conv.get("messages", [])

    def get_recent_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[dict]:
        """Retrieves the N recent messages for context window sliding."""
        history = self.load_history(conversation_id)
        n = limit if limit is not None else self.max_messages
        latest = history[-n:] if len(history) > n else history
        logger.info(f"[Memory Service] Loaded {len(latest)} recent messages for conversation '{conversation_id}' (limit: {n})")
        return latest

    def getRecentMessages(self, conversation_id: str, limit: Optional[int] = None) -> List[dict]:
        """Alias for get_recent_messages."""
        return self.get_recent_messages(conversation_id=conversation_id, limit=limit)

    def get_latest_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[dict]:
        """Alias for get_recent_messages."""
        return self.get_recent_messages(conversation_id=conversation_id, limit=limit)

    def format_history_for_prompt(self, conversation_id: str, limit: Optional[int] = None) -> str:
        """Formats the latest messages into a clean prompt string."""
        messages = self.get_recent_messages(conversation_id, limit=limit)
        if not messages:
            return ""
        
        lines = []
        for msg in messages:
            role_title = "Customer" if msg.get("role") == "user" else "AI"
            lines.append(f"{role_title}: {msg.get('content', '')}")
        return "\n".join(lines)

memory_service = MemoryService()
