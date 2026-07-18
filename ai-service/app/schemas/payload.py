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
    python: str = Field(..., example="running")
    timestamp: str = Field(..., example="2026-07-18T12:00:00Z")
    uptime: str = Field(..., example="120s")

# 4. Chat Schemas
class ChatRequest(BaseModel):
    message: Optional[str] = Field(default="Hello", example="I was charged twice for my subscription this month.")
    conversation_id: Optional[str] = Field(default="conv_default_001", example="conv_default_001")
    customer_id: Optional[str] = Field(default="cust_1001", example="cust_1001")

class DummyChatResponse(BaseModel):
    success: bool = Field(True, example=True)
    message: str = Field("AI endpoint working", example="AI endpoint working")
    response: str = Field("Hello from AI Service", example="Hello from AI Service")

class ChatResponse(BaseModel):
    response: str = Field(..., example="I apologize for the double charge. I have processed a refund of $49.99.")
    conversation_id: str = Field(..., example="conv_default_001")
    intent_detected: str = Field(..., example="Billing & Refunds")
    confidence: float = Field(..., example=0.98)

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
