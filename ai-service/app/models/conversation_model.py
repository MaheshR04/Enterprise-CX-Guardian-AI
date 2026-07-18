from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ConversationModel(BaseModel):
    """
    MongoDB Conversation Document Model.

    Stored in: CONVERSATION_COLLECTION (default: "conversations")

    Represents a lightweight conversation session header document.
    Messages are stored separately in MESSAGE_COLLECTION to support
    scalable, paginated access and future RAG pipeline integration.
    """

    conversation_id: str = Field(
        ...,
        alias="conversationId",
        description="Unique UUID identifying the conversation session.",
        example="conv_7a8b9c0d-1234-5678-abcd-ef0123456789"
    )
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="ISO 8601 timestamp when the conversation session was first created.",
        example="2026-07-18T14:30:00.000000"
    )
    updated_at: str = Field(
        ...,
        alias="updatedAt",
        description="ISO 8601 timestamp of the most recent message or update.",
        example="2026-07-18T14:35:00.000000"
    )
    status: str = Field(
        default="active",
        description="Lifecycle state of the conversation. One of: active | archived | deleted.",
        example="active"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description=(
            "Extensible key-value metadata attached to this conversation session. "
            "May include channel, source, customer_id, language, or custom enterprise fields."
        ),
        example={
            "channel": "web",
            "source": "enterprise_cx",
            "language": "en"
        }
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "conversationId": "conv_7a8b9c0d-1234-5678-abcd-ef0123456789",
                "createdAt": "2026-07-18T14:30:00.000000",
                "updatedAt": "2026-07-18T14:35:00.000000",
                "status": "active",
                "metadata": {
                    "channel": "web",
                    "source": "enterprise_cx",
                    "language": "en"
                }
            }
        }
