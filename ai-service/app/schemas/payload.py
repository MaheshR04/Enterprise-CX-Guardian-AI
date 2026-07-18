from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# 1. Standard Success Schema
class StandardResponse(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("", example="Success")
    data: Optional[Any] = Field(default_factory=dict)

# 2. Standard Error Schema
class ErrorResponse(BaseModel):
    success: bool = Field(False, example=False)
    message: str = Field("", example="Operational Error")
    error: str = Field("", example="Error description")

# 3. Health Schema
class HealthResponse(BaseModel):
    status: str = Field(..., example="healthy")
    service: str = Field(..., example="Enterprise CX Guardian AI")
    version: str = Field(..., example="1.0.0")
    uptime: str = Field(..., example="120s")
    timestamp: str = Field(..., example="2026-07-18T12:00:00Z")
    python: str = Field(..., example="running")

# 4. Chat Schemas
class ChatRequest(BaseModel):
    message: Optional[str] = Field(default="Hello AI", example="Hello AI")
    conversationId: Optional[str] = Field(default="conv_default_001", example="conv_default_001")
    conversation_id: Optional[str] = Field(default=None, example="conv_default_001")
    temperature: Optional[float] = Field(default=None, example=0.2)

class TokenUsage(BaseModel):
    prompt_tokens: Optional[int] = Field(default=0, example=10)
    completion_tokens: Optional[int] = Field(default=0, example=12)
    total_tokens: Optional[int] = Field(default=0, example=22)

class ChatResponseData(BaseModel):
    reply: str = Field(..., example="Hello from Groq LLaMA-3")
    model: str = Field(..., example="llama3-70b-8192")
    usage: Optional[TokenUsage] = Field(default=None)
    processingTime: str = Field(..., example="15ms")

class ChatResponsePayload(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("AI response generated successfully", example="AI response generated successfully")
    data: ChatResponseData

class ChatConnectivityData(BaseModel):
    reply: str = Field("Hello from FastAPI", example="Hello from FastAPI")
    service: str = Field("Python AI Service", example="Python AI Service")
    version: str = Field("1.0.0", example="1.0.0")
    processingTime: str = Field("15ms", example="15ms")

class ChatConnectivityResponse(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("AI service connected successfully", example="AI service connected successfully")
    data: ChatConnectivityData

class DummyChatResponse(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("AI endpoint working", example="AI endpoint working")
    response: str = Field("Hello from AI Service", example="Hello from AI Service")

class ChatResponse(BaseModel):
    reply: str = Field(..., example="Hello from Groq LLaMA-3")
    model: str = Field(..., example="llama3-70b-8192")
    usage: Optional[TokenUsage] = Field(default=None)
    processingTime: str = Field(..., example="15ms")

# 5. Reasoning Schemas
class ReasoningRequest(BaseModel):
    issue_description: str = Field(..., example="Customer account locked after 3 failed password attempts.")
    ticket_id: Optional[str] = Field(default="CX-4912", example="CX-4912")

class ReasoningResponse(BaseModel):
    ticket_id: str = Field(..., example="CX-4912")
    root_cause: str = Field(..., example="Automated security lockout triggered by repeated invalid authorization attempts.")
    recommended_action: str = Field(..., example="Trigger secure OTP password reset link to customer email.")
    confidence_score: float = Field(..., example=0.95)

# 6. Sentiment Schemas
class SentimentRequest(BaseModel):
    text: str = Field(..., example="Your product is amazing, but customer support took 3 days to reply.")

class SentimentResponse(BaseModel):
    sentiment: str = Field(..., example="Mixed")
    polarity_score: float = Field(..., example=0.2)
    emotions_detected: List[str] = Field(..., example=["Satisfaction", "Frustration"])

# 7. Recommendation Schemas
class RecommendationRequest(BaseModel):
    customer_tier: str = Field(..., example="Enterprise Gold")
    account_age_months: int = Field(..., example=24)
    ticket_subject: str = Field(..., example="Downtime SLA breach credit request")

class RecommendationResponse(BaseModel):
    action: str = Field(..., example="Issue $200 SLA Service Credit")
    priority: str = Field(..., example="High")
    explanation: str = Field(..., example="High-value enterprise customer with 24-month tenure eligible for automated SLA compensation.")
