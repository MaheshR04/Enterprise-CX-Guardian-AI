from fastapi import APIRouter, Depends, status
from typing import List, Dict, Any
from app.schemas.payload import ErrorResponse
from app.conversation.conversation_manager import conversation_manager, ConversationManager
from app.utils.exceptions import ConversationNotFoundException

router = APIRouter()

def get_conversation_manager() -> ConversationManager:
    """Dependency injection provider for ConversationManager."""
    return conversation_manager

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="List All Active Conversations",
    description="Returns summary metadata list of all active in-memory conversations.",
    responses={
        200: {"description": "List of active conversations retrieved successfully."}
    }
)
async def list_conversations(
    mgr: ConversationManager = Depends(get_conversation_manager)
) -> Dict[str, Any]:
    """
    Asynchronously retrieves a summary list of all conversations.
    """
    conversations_list = mgr.list_conversations()
    return {
        "success": True,
        "message": "Conversations retrieved successfully",
        "data": {
            "conversations": conversations_list,
            "total_count": len(conversations_list)
        }
    }

@router.get(
    "/{conversationId}",
    status_code=status.HTTP_200_OK,
    summary="Get Conversation By ID",
    description="Retrieves a specific conversation session including complete message history.",
    responses={
        200: {"description": "Conversation details retrieved successfully."},
        404: {"model": ErrorResponse, "description": "Conversation ID not found."}
    }
)
async def get_conversation(
    conversationId: str,
    mgr: ConversationManager = Depends(get_conversation_manager)
) -> Dict[str, Any]:
    """
    Asynchronously retrieves details for a single conversation ID.
    Raises ConversationNotFoundException if ID is missing.
    """
    conv = mgr.get_conversation(conversationId)
    if not conv:
        raise ConversationNotFoundException(conversation_id=conversationId)

    return {
        "success": True,
        "message": "Conversation details retrieved successfully",
        "data": conv
    }

@router.delete(
    "/{conversationId}",
    status_code=status.HTTP_200_OK,
    summary="Delete Conversation By ID",
    description="Deletes a conversation session and clears its message history.",
    responses={
        200: {"description": "Conversation deleted successfully."},
        404: {"model": ErrorResponse, "description": "Conversation ID not found."}
    }
)
async def delete_conversation(
    conversationId: str,
    mgr: ConversationManager = Depends(get_conversation_manager)
) -> Dict[str, Any]:
    """
    Asynchronously deletes a single conversation session by ID.
    Raises ConversationNotFoundException if ID is missing.
    """
    deleted = mgr.delete_conversation(conversationId)
    if not deleted:
        raise ConversationNotFoundException(conversation_id=conversationId)

    return {
        "success": True,
        "message": f"Conversation '{conversationId}' deleted successfully",
        "data": {"conversation_id": conversationId}
    }
