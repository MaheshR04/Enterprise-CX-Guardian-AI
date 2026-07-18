from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class MessageModel(BaseModel):
    """
    MongoDB Message Document Model.
    Represents a single user or assistant message within a conversation session.
    """
    message_id: str = Field(
        ...,
        alias="messageId",
        description="Unique UUID for this message.",
        example="msg_8f1b2c3d-5678-1234-efab-cd0123456789"
    )
    conversation_id: str = Field(
        ...,
        alias="conversationId",
        description="Parent conversation session UUID.",
        example="conv_7a8b9c0d-1234-5678-abcd-ef0123456789"
    )
    role: str = Field(
        ...,
        description="Message author role. One of: user | assistant | system.",
        example="user"
    )
    content: str = Field(
        ...,
        description="Full text content of the message.",
        example="Hello, how can you help me?"
    )
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp when the message was created.",
        example="2026-07-18T14:35:00.000000"
    )
    tokens: Optional[Dict[str, int]] = Field(
        default_factory=dict,
        description="Per-message token accounting (prompt_tokens, completion_tokens)."
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Extensible key-value metadata attached to the message."
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "messageId": "msg_8f1b2c3d-5678-1234-efab-cd0123456789",
                "conversationId": "conv_7a8b9c0d-1234-5678-abcd-ef0123456789",
                "role": "user",
                "content": "Hello, how can you help me?",
                "timestamp": "2026-07-18T14:35:00.000000",
                "tokens": {},
                "metadata": {}
            }
        }
