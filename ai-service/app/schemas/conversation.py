from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.schemas.message import Message

class Conversation(BaseModel):
    conversationId: str = Field(..., example="conv_7a8b9c0d")
    createdAt: str = Field(..., example="2026-07-18T14:30:00.000Z")
    updatedAt: str = Field(..., example="2026-07-18T14:35:00.000Z")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    messages: List[Message] = Field(default_factory=list)
