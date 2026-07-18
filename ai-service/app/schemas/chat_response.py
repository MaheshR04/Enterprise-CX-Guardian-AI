from pydantic import BaseModel, Field
from typing import Optional

class TokenUsage(BaseModel):
    prompt_tokens: Optional[int] = Field(default=0, example=10)
    completion_tokens: Optional[int] = Field(default=0, example=12)
    total_tokens: Optional[int] = Field(default=0, example=22)

class ChatResponseData(BaseModel):
    conversationId: str = Field(..., example="conv_7a8b9c0d")
    messageId: str = Field(..., example="msg_8f1b2c3d")
    reply: str = Field(..., example="Hello from Groq LLaMA-3")
    processingTime: str = Field(..., example="15ms")
    model: str = Field(..., example="llama3-70b-8192")
    historyLength: int = Field(..., example=6)
    usage: Optional[TokenUsage] = Field(default=None)

class ChatResponsePayload(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("Response generated successfully", example="Response generated successfully")
    data: ChatResponseData
