from fastapi import APIRouter, Depends, Query, status
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.conversation.conversation_manager import conversation_manager, ConversationManager
from app.utils.exceptions import (
    ConversationNotFoundException,
    InvalidConversationIdException,
    InvalidStatusException,
)
from app.schemas.payload import ErrorResponse

router = APIRouter()


class CreateConversationRequest(BaseModel):
    conversationId: Optional[str] = Field(
        default=None,
        description="Optional client-supplied conversation ID. Generated when omitted.",
        example="conv_enterprise_demo_001"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional enterprise metadata for channel, customer, source, or tenant context.",
        example={"channel": "web", "customer_id": "cust_1001", "tenant": "enterprise"}
    )


def get_conversation_manager() -> ConversationManager:
    """Dependency injection provider for ConversationManager."""
    return conversation_manager


# ======================================================================
# POST /api/v1/conversations
# ======================================================================
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create Conversation",
    description=(
        "Creates a conversation header in MongoDB without sending a chat message. "
        "Use POST /api/v1/chat with the returned conversation_id to continue it."
    ),
    responses={
        201: {"description": "Conversation created successfully."},
        400: {"model": ErrorResponse, "description": "Invalid Conversation ID."},
        409: {"model": ErrorResponse, "description": "Conversation ID already exists."}
    }
)
async def create_conversation(
    payload: CreateConversationRequest,
    mgr: ConversationManager = Depends(get_conversation_manager)
) -> Dict[str, Any]:
    """Creates a new MongoDB-backed conversation session."""
    if payload.conversationId and len(payload.conversationId) > 128:
        raise InvalidConversationIdException(
            detail="Conversation ID must be a non-empty string under 128 characters."
        )

    conversation = await mgr.create_conversation(
        conversation_id=payload.conversationId,
        metadata=payload.metadata
    )

    return {
        "success": True,
        "message": "Conversation created successfully",
        "data": conversation
    }


# ======================================================================
# GET /api/v1/conversations
# ======================================================================
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="List All Conversations",
    description=(
        "Returns a paginated list of conversation sessions stored in MongoDB. "
        "Supports limit, page, and sort query parameters."
    ),
    responses={
        200: {"description": "Conversations retrieved successfully."}
    }
)
async def list_conversations(
    limit: int = Query(default=20,  ge=1, le=100, description="Number of conversations per page."),
    page:  int = Query(default=1,   ge=1,          description="Page number (1-indexed)."),
    sort:  str = Query(default="desc",              description="Sort order: 'desc' (newest first) or 'asc' (oldest first)."),
    mgr:   ConversationManager = Depends(get_conversation_manager)
) -> Dict[str, Any]:
    """
    Retrieves paginated conversations from MongoDB.
    Internally: Router → ConversationManager → MemoryService → ConversationRepository → MongoDB.
    """
    if sort not in ("asc", "desc"):
        sort = "desc"

    result = await mgr.list_conversations(limit=limit, page=page, sort=sort)
    return {
        "success": True,
        "message": "Conversations retrieved successfully",
        "data": {
            "conversations": result["conversations"],
            "pagination": {
                "total_count":  result["total_count"],
                "page":         result["page"],
                "limit":        result["limit"],
                "total_pages":  result["total_pages"]
            }
        }
    }


# ======================================================================
# GET /api/v1/conversations/search
# ======================================================================
@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    summary="Search Conversations",
    description=(
        "Search conversation sessions stored in MongoDB by conversationId, status, "
        "and/or date range. All filters are optional and combinable. "
        "Results are paginated and enriched with message_count."
    ),
    responses={
        200: {"description": "Search results retrieved successfully."}
    }
)
async def search_conversations(
    conversationId: Optional[str] = Query(default=None, description="Partial case-insensitive match on conversationId."),
    status_filter:  Optional[str] = Query(default=None, alias="status", description="Exact status match: active | archived | deleted."),
    date_from:      Optional[str] = Query(default=None, description="ISO 8601 start date. e.g. 2026-07-01T00:00:00"),
    date_to:        Optional[str] = Query(default=None, description="ISO 8601 end date.   e.g. 2026-07-18T23:59:59"),
    limit:          int           = Query(default=20, ge=1, le=100, description="Documents per page."),
    page:           int           = Query(default=1,  ge=1,         description="Page number (1-indexed)."),
    sort:           str           = Query(default="desc",           description="Sort order: 'desc' or 'asc'."),
    mgr: ConversationManager = Depends(get_conversation_manager)
) -> Dict[str, Any]:
    """
    Searches MongoDB conversations using any combination of:
    - conversationId (partial match)
    - status         (active | closed | archived)
    - date_from / date_to (ISO 8601 range on createdAt)
    """
    if sort not in ("asc", "desc"):
        sort = "desc"

    # Validate status if provided
    valid_statuses = {"active", "archived", "deleted"}
    if status_filter and status_filter.lower() not in valid_statuses:
        raise InvalidStatusException(status_filter)

    result = await mgr.search_conversations(
        conversation_id=conversationId,
        status=status_filter,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        page=page,
        sort=sort
    )
    return {
        "success": True,
        "message": "Search results retrieved successfully",
        "data": {
            "conversations": result["conversations"],
            "filters": {
                "conversationId": conversationId,
                "status":         status_filter,
                "date_from":      date_from,
                "date_to":        date_to
            },
            "pagination": {
                "total_count":  result["total_count"],
                "page":         result["page"],
                "limit":        result["limit"],
                "total_pages":  result["total_pages"]
            }
        }
    }


# ======================================================================
# GET /api/v1/conversations/{conversationId}
# ======================================================================
@router.get(
    "/{conversationId}",
    status_code=status.HTTP_200_OK,
    summary="Get Conversation By ID",
    description=(
        "Retrieves a specific conversation session from MongoDB by conversationId, "
        "including metadata, messages, prompt stats, and usage telemetry summary."
    ),
    responses={
        200: {"description": "Conversation retrieved successfully."},
        400: {"model": ErrorResponse, "description": "Invalid Conversation ID."},
        404: {"model": ErrorResponse, "description": "Conversation not found."}
    }
)
async def get_conversation(
    conversationId: str,
    mgr: ConversationManager = Depends(get_conversation_manager)
) -> Dict[str, Any]:
    """
    Retrieves a single conversation document from MongoDB.
    Raises ConversationNotFoundException if not found.
    """
    if not conversationId or len(conversationId) > 128:
        raise InvalidConversationIdException(
            detail="Conversation ID must be a non-empty string under 128 characters."
        )

    conv = await mgr.get_conversation(conversationId)
    if not conv:
        raise ConversationNotFoundException(conversation_id=conversationId)

    return {
        "success": True,
        "message": "Conversation retrieved successfully",
        "data":    conv
    }


# ======================================================================
# DELETE /api/v1/conversations/{conversationId}  — SOFT DELETE
# ======================================================================
@router.delete(
    "/{conversationId}",
    status_code=status.HTTP_200_OK,
    summary="Soft Delete Conversation",
    description=(
        "Soft-deletes a conversation by setting its status to DELETED. "
        "The MongoDB document is NEVER permanently removed. "
        "Soft-deleted conversations are excluded from all list and search results. "
        "Use PATCH /{conversationId}/restore to undo."
    ),
    responses={
        200: {"description": "Conversation soft-deleted successfully."},
        400: {"model": ErrorResponse, "description": "Invalid Conversation ID."},
        404: {"model": ErrorResponse, "description": "Conversation not found."}
    }
)
async def delete_conversation(
    conversationId: str,
    mgr: ConversationManager = Depends(get_conversation_manager)
) -> Dict[str, Any]:
    """Soft-deletes a conversation: status → DELETED. Document preserved in MongoDB."""
    if not conversationId or len(conversationId) > 128:
        raise InvalidConversationIdException(
            detail="Conversation ID must be a non-empty string under 128 characters."
        )

    deleted = await mgr.delete_conversation(conversationId)
    if not deleted:
        raise ConversationNotFoundException(conversation_id=conversationId)

    return {
        "success": True,
        "message": f"Conversation '{conversationId}' soft-deleted successfully",
        "data": {
            "conversation_id": conversationId,
            "status":          "deleted"
        }
    }


# ======================================================================
# PATCH /api/v1/conversations/{conversationId}/archive
# ======================================================================
@router.patch(
    "/{conversationId}/archive",
    status_code=status.HTTP_200_OK,
    summary="Archive Conversation",
    description=(
        "Archives a conversation by setting its status to ARCHIVED. "
        "Archived conversations remain visible in list and search results "
        "but are no longer considered active."
    ),
    responses={
        200: {"description": "Conversation archived successfully."},
        400: {"model": ErrorResponse, "description": "Invalid Conversation ID."},
        404: {"model": ErrorResponse, "description": "Conversation not found."}
    }
)
async def archive_conversation(
    conversationId: str,
    mgr: ConversationManager = Depends(get_conversation_manager)
) -> Dict[str, Any]:
    """Archives a conversation: status → ARCHIVED."""
    if not conversationId or len(conversationId) > 128:
        raise InvalidConversationIdException(
            detail="Conversation ID must be a non-empty string under 128 characters."
        )

    archived = await mgr.archive_conversation(conversationId)
    if not archived:
        raise ConversationNotFoundException(conversation_id=conversationId)

    return {
        "success": True,
        "message": f"Conversation '{conversationId}' archived successfully",
        "data": {
            "conversation_id": conversationId,
            "status":          "archived"
        }
    }


# ======================================================================
# PATCH /api/v1/conversations/{conversationId}/restore
# ======================================================================
@router.patch(
    "/{conversationId}/restore",
    status_code=status.HTTP_200_OK,
    summary="Restore Conversation",
    description=(
        "Restores a DELETED or ARCHIVED conversation back to ACTIVE status. "
        "The conversation will reappear in all list and search results."
    ),
    responses={
        200: {"description": "Conversation restored successfully."},
        400: {"model": ErrorResponse, "description": "Invalid Conversation ID."},
        404: {"model": ErrorResponse, "description": "Conversation not found."}
    }
)
async def restore_conversation(
    conversationId: str,
    mgr: ConversationManager = Depends(get_conversation_manager)
) -> Dict[str, Any]:
    """Restores a DELETED or ARCHIVED conversation: status → ACTIVE."""
    if not conversationId or len(conversationId) > 128:
        raise InvalidConversationIdException(
            detail="Conversation ID must be a non-empty string under 128 characters."
        )

    restored = await mgr.restore_conversation(conversationId)
    if not restored:
        raise ConversationNotFoundException(conversation_id=conversationId)

    return {
        "success": True,
        "message": f"Conversation '{conversationId}' restored to active successfully",
        "data": {
            "conversation_id": conversationId,
            "status":          "active"
        }
    }
