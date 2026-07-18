import uuid
from typing import List, Optional, Dict, Any
from app.memory.memory_service import memory_service, MemoryService
from app.core.logger import logger


class ConversationManager:
    """
    Conversation Manager for Enterprise CX Guardian AI.

    Acts as the single facade between controllers/routers and the MongoDB
    persistence layer. Controllers call ConversationManager methods only —
    they have zero knowledge that MongoDB exists.

    All storage operations are delegated to MemoryService, which in turn
    delegates to ConversationRepository and MessageRepository.
    """

    def __init__(self, memory: MemoryService = None):
        self._memory: MemoryService = memory or memory_service

    # ------------------------------------------------------------------
    # ID Generation
    # ------------------------------------------------------------------

    def generate_conversation_id(self) -> str:
        """Generates a new unique conversation UUID."""
        return f"conv_{uuid.uuid4()}"

    def generate_message_id(self) -> str:
        """Generates a new unique message UUID."""
        return f"msg_{uuid.uuid4()}"

    # ------------------------------------------------------------------
    # Conversation Lifecycle
    # ------------------------------------------------------------------

    async def create_conversation(
        self,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Creates a new conversation session.
        Delegates storage to MemoryService → ConversationRepository → MongoDB.
        """
        cid = conversation_id or self.generate_conversation_id()
        doc = await self._memory.createConversation(
            conversation_id=cid,
            metadata=metadata
        )
        logger.info(f"[ConversationManager] Created conversation '{cid}'")
        return doc

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a conversation session by ID.
        Returns None if not found.
        """
        return await self._memory.loadConversation(conversation_id)

    async def conversation_exists(self, conversation_id: str) -> bool:
        """
        Returns True if the conversation session exists.
        """
        return await self._memory.conversationExists(conversation_id)

    async def conversation_exists_any(self, conversation_id: str) -> bool:
        """
        Returns True if the conversation exists in any status, including deleted.
        """
        return await self._memory.conversationExistsAny(conversation_id)

    async def list_conversations(
        self,
        limit: int = 20,
        page: int = 1,
        sort: str = "desc"
    ) -> Dict[str, Any]:
        """
        Returns a paginated summary of all conversation sessions
        enriched with message_count.
        """
        return await self._memory.listConversations(
            limit=limit,
            page=page,
            sort=sort
        )

    async def search_conversations(
        self,
        conversation_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 20,
        page: int = 1,
        sort: str = "desc"
    ) -> Dict[str, Any]:
        """
        Searches conversation sessions by conversationId, status, and date range.
        Results are paginated and enriched with message_count.

        Args:
            conversation_id: Partial case-insensitive ID match.
            status:          Exact match. One of: active | closed | archived.
            date_from:       ISO 8601 start date (e.g. '2026-07-01T00:00:00').
            date_to:         ISO 8601 end date   (e.g. '2026-07-18T23:59:59').
            limit:           Documents per page (default 20).
            page:            1-indexed page number (default 1).
            sort:            'desc' newest first | 'asc' oldest first.
        """
        return await self._memory.searchConversations(
            conversation_id=conversation_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            page=page,
            sort=sort
        )

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Soft-deletes a conversation by setting status=DELETED.
        The MongoDB document is NEVER permanently removed.
        Soft-deleted conversations disappear from all list/search results.
        Returns True if soft-deleted, False if not found.
        """
        deleted = await self._memory.deleteConversation(conversation_id)
        if deleted:
            logger.info(
                f"[ConversationManager] Soft-deleted conversation '{conversation_id}' "
                f"[status=deleted]"
            )
        return deleted

    async def archive_conversation(self, conversation_id: str) -> bool:
        """
        Archives a conversation by setting status=ARCHIVED.
        Archived conversations remain visible in list/search results.
        Returns True if archived, False if not found.
        """
        archived = await self._memory.archiveConversation(conversation_id)
        if archived:
            logger.info(
                f"[ConversationManager] Archived conversation '{conversation_id}' "
                f"[status=archived]"
            )
        return archived

    async def restore_conversation(self, conversation_id: str) -> bool:
        """
        Restores a DELETED or ARCHIVED conversation back to ACTIVE status.
        Returns True if restored, False if not found.
        """
        restored = await self._memory.restoreConversation(conversation_id)
        if restored:
            logger.info(
                f"[ConversationManager] Restored conversation '{conversation_id}' "
                f"[status=active]"
            )
        return restored

    async def clear_conversation(self, conversation_id: str) -> bool:
        """
        Clears all messages in a conversation without deleting
        the conversation document itself.
        """
        cleared = await self._memory.clearConversation(conversation_id)
        if cleared:
            logger.info(f"[ConversationManager] Cleared messages in conversation '{conversation_id}'")
        return cleared

    # ------------------------------------------------------------------
    # Message Operations
    # ------------------------------------------------------------------

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Persists a message (user | assistant | system) to the conversation.
        Auto-creates the conversation if it does not exist yet.
        """
        exists = await self.conversation_exists(conversation_id)
        if not exists:
            await self.create_conversation(conversation_id=conversation_id)

        msg = await self._memory.saveMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata=metadata
        )
        logger.info(
            f"[ConversationManager] Saved '{role}' message '{msg.get('message_id')}' "
            f"to conversation '{conversation_id}'"
        )
        return msg

    async def get_recent_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the N most recent messages for context window injection.
        Bounded by MAX_HISTORY from settings.
        """
        return await self._memory.getRecentMessages(
            conversation_id=conversation_id,
            limit=limit
        )

    async def format_history_for_prompt(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> str:
        """
        Formats recent conversation history into a clean multi-turn
        dialogue string ready for PromptBuilder injection.
        """
        return await self._memory.formatHistoryForPrompt(
            conversation_id=conversation_id,
            limit=limit
        )


conversation_manager = ConversationManager()
