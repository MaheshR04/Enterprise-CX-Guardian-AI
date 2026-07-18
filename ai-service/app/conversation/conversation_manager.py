import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from app.core.config import settings
from app.core.logger import logger

class ConversationManager:
    """
    In-Memory Conversation & History Manager for Enterprise CX Guardian AI.
    Supports MAX_CONVERSATIONS capacity limits and AUTO_DELETE_EMPTY cleanup logic.
    """
    def __init__(self):
        # In-memory storage dictionary: { conversation_id: { "id": str, "created_at": str, "updated_at": str, "messages": [] } }
        self._conversations: Dict[str, Dict[str, Any]] = {}

    def create_conversation_id(self) -> str:
        """Generates a unique conversation UUID."""
        return f"conv_{uuid.uuid4()}"

    def create_message_id(self) -> str:
        """Generates a unique message UUID."""
        return f"msg_{uuid.uuid4()}"

    def create_conversation(self, conversation_id: Optional[str] = None, metadata: Optional[dict] = None) -> dict:
        """
        Creates and stores a new conversation session.
        Enforces MAX_CONVERSATIONS capacity by evicting oldest sessions.
        """
        # Enforce MAX_CONVERSATIONS limit
        if len(self._conversations) >= settings.MAX_CONVERSATIONS:
            oldest_id = next(iter(self._conversations))
            del self._conversations[oldest_id]
            logger.info(f"[Conversation Manager] Capacity limit MAX_CONVERSATIONS ({settings.MAX_CONVERSATIONS}) reached. Evicted oldest session '{oldest_id}'.")

        cid = conversation_id or self.create_conversation_id()
        now_iso = datetime.utcnow().isoformat()
        
        conversation = {
            "conversation_id": cid,
            "created_at": now_iso,
            "updated_at": now_iso,
            "metadata": metadata or {},
            "messages": []
        }
        
        self._conversations[cid] = conversation
        logger.info(f"[Conversation Manager] Created conversation session ID: {cid}")
        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[dict]:
        """
        Retrieves a conversation by conversation ID.
        """
        return self._conversations.get(conversation_id)

    def append_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Appends a message (user, assistant, system) to an existing conversation session.
        Auto-creates conversation session if it doesn't exist yet.
        """
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            conversation = self.create_conversation(conversation_id=conversation_id)

        mid = self.create_message_id()
        now_iso = datetime.utcnow().isoformat()

        message = {
            "message_id": mid,
            "role": role,
            "content": content,
            "timestamp": now_iso,
            "metadata": metadata or {}
        }

        conversation["messages"].append(message)
        conversation["updated_at"] = now_iso
        
        logger.info(f"[Conversation Manager] Appended '{role}' message ({mid}) to conversation {conversation_id}")
        return message

    def list_conversations(self) -> List[dict]:
        """
        Lists summary metadata of all active conversations.
        Performs AUTO_DELETE_EMPTY cleanup if enabled.
        """
        if settings.AUTO_DELETE_EMPTY:
            empty_ids = [cid for cid, conv in self._conversations.items() if not conv.get("messages")]
            for cid in empty_ids:
                del self._conversations[cid]
                logger.info(f"[Conversation Manager] AUTO_DELETE_EMPTY cleaned empty session '{cid}'")

        summaries = []
        for cid, conv in self._conversations.items():
            summaries.append({
                "conversation_id": cid,
                "created_at": conv.get("created_at"),
                "updated_at": conv.get("updated_at"),
                "message_count": len(conv.get("messages", []))
            })
        return summaries

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Deletes a conversation session by ID.
        """
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            logger.info(f"[Conversation Manager] Deleted conversation session ID: {conversation_id}")
            return True
        return False

conversation_manager = ConversationManager()
