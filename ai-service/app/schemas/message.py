from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class Message(BaseModel):
    messageId: str = Field(..., example="msg_8f1b2c3d")
    role: str = Field(..., example="user")
    content: str = Field(..., example="Hello AI")
    timestamp: str = Field(..., example="2026-07-18T14:35:00.000Z")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
