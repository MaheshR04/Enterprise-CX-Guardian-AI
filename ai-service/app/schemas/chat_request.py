from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: Optional[str] = Field(default="Hello AI", example="Hello AI")
    conversationId: Optional[str] = Field(default=None, example="conv_7a8b9c0d")
    conversation_id: Optional[str] = Field(default=None, example="conv_7a8b9c0d")
    temperature: Optional[float] = Field(default=None, example=0.2)
