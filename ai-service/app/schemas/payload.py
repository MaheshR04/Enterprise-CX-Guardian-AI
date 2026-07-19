"""
Enterprise CX Guardian AI — OpenAPI / Swagger Data Schemas
===========================================================

Defines request/response models with Pydantic v2 metadata, field descriptions,
and rich OpenAPI JSON schema examples for interactive Swagger documentation (/docs).
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# ── 1. Standard API Responses ──────────────────────────────────────

class StandardResponse(BaseModel):
    success: bool = Field(True, description="Indicates if operation succeeded", json_schema_extra={"example": True})
    message: str = Field("", description="Human-readable summary message", json_schema_extra={"example": "Operation executed successfully"})
    data: Optional[Any] = Field(default_factory=dict, description="Response payload data")


class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Always false for error responses", json_schema_extra={"example": False})
    message: str = Field("", description="High-level error summary", json_schema_extra={"example": "Request execution failed"})
    error: str = Field("", description="Detailed error cause or validation trace", json_schema_extra={"example": "Invalid parameter provided"})
    error_code: Optional[str] = Field("OPERATIONAL_ERROR", description="Machine-readable error code", json_schema_extra={"example": "OPERATIONAL_ERROR"})


# ── 2. System Health & Monitoring Schemas ───────────────────────────

class HealthResponse(BaseModel):
    status: str = Field(..., description="System operational status", json_schema_extra={"example": "healthy"})
    service: str = Field(..., description="Microservice name", json_schema_extra={"example": "Enterprise CX Guardian AI"})
    version: str = Field(..., description="Application version", json_schema_extra={"example": "1.0.0"})
    uptime: str = Field(..., description="Formatted uptime duration", json_schema_extra={"example": "1d 4h 12m"})
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp", json_schema_extra={"example": "2026-07-19T22:00:00Z"})
    python: str = Field(..., description="Python process state", json_schema_extra={"example": "running"})


# ── 3. Chat & LLM Schemas ───────────────────────────────────────────

class ChatRequest(BaseModel):
    message: Optional[str] = Field(
        default="Hello AI",
        description="User query or message text",
        json_schema_extra={"example": "How do I upgrade my enterprise SLA account?"}
    )
    conversationId: Optional[str] = Field(
        default="conv_default_001",
        description="Unique session identifier (camelCase variant)",
        json_schema_extra={"example": "conv_99a41b80"}
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Unique session identifier (snake_case variant)",
        json_schema_extra={"example": "conv_99a41b80"}
    )
    temperature: Optional[float] = Field(
        default=0.2,
        ge=0.0,
        le=1.0,
        description="LLM sampling temperature (0.0=deterministic, 1.0=creative)",
        json_schema_extra={"example": 0.2}
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "How do I reset my API key?",
                "conversationId": "conv_usr_8812a",
                "temperature": 0.2
            }
        }
    }


class TokenUsage(BaseModel):
    prompt_tokens: Optional[int] = Field(default=0, description="Tokens consumed by context and prompt", json_schema_extra={"example": 42})
    completion_tokens: Optional[int] = Field(default=0, description="Tokens generated in LLM reply", json_schema_extra={"example": 88})
    total_tokens: Optional[int] = Field(default=0, description="Total tokens consumed", json_schema_extra={"example": 130})


class ChatResponseData(BaseModel):
    reply: str = Field(..., description="Generated AI assistant response text", json_schema_extra={"example": "You can reset your API key in the Security Settings tab."})
    model: str = Field(..., description="Groq AI model utilized for completion", json_schema_extra={"example": "llama3-70b-8192"})
    usage: Optional[TokenUsage] = Field(default=None, description="Token consumption telemetry")
    processingTime: str = Field(..., description="Total execution latency in milliseconds", json_schema_extra={"example": "45ms"})


class ChatResponsePayload(BaseModel):
    success: bool = Field(True, json_schema_extra={"example": True})
    message: str = Field("AI response generated successfully", json_schema_extra={"example": "AI response generated successfully"})
    data: ChatResponseData


class ChatConnectivityData(BaseModel):
    reply: str = Field("Hello from FastAPI", json_schema_extra={"example": "Hello from FastAPI"})
    service: str = Field("Python AI Service", json_schema_extra={"example": "Python AI Service"})
    version: str = Field("1.0.0", json_schema_extra={"example": "1.0.0"})
    processingTime: str = Field("15ms", json_schema_extra={"example": "15ms"})


class ChatConnectivityResponse(BaseModel):
    success: bool = Field(True, json_schema_extra={"example": True})
    message: str = Field("AI service connected successfully", json_schema_extra={"example": "AI service connected successfully"})
    data: ChatConnectivityData


class DummyChatResponse(BaseModel):
    success: bool = Field(True, json_schema_extra={"example": True})
    message: str = Field("AI endpoint working", json_schema_extra={"example": "AI endpoint working"})
    response: str = Field("Hello from AI Service", json_schema_extra={"example": "Hello from AI Service"})


class ChatResponse(BaseModel):
    reply: str = Field(..., json_schema_extra={"example": "Hello from Groq LLaMA-3"})
    model: str = Field(..., json_schema_extra={"example": "llama3-70b-8192"})
    usage: Optional[TokenUsage] = Field(default=None)
    processingTime: str = Field(..., json_schema_extra={"example": "45ms"})


# ── 4. AI Tool & Intelligence Schemas ───────────────────────────────

class ReasoningRequest(BaseModel):
    issue_description: str = Field(..., description="Customer problem description", json_schema_extra={"example": "Customer account locked after 3 failed password attempts."})
    ticket_id: Optional[str] = Field(default="CX-4912", description="Ticket reference number", json_schema_extra={"example": "CX-4912"})


class ReasoningResponse(BaseModel):
    ticket_id: str = Field(..., json_schema_extra={"example": "CX-4912"})
    root_cause: str = Field(..., json_schema_extra={"example": "Automated security lockout triggered by repeated invalid authorization attempts."})
    recommended_action: str = Field(..., json_schema_extra={"example": "Trigger secure OTP password reset link to customer email."})
    confidence_score: float = Field(..., json_schema_extra={"example": 0.95})


class SentimentRequest(BaseModel):
    text: str = Field(..., description="Customer feedback or conversation text", json_schema_extra={"example": "Your product is amazing, but customer support took 3 days to reply."})


class SentimentResponse(BaseModel):
    sentiment: str = Field(..., json_schema_extra={"example": "Mixed"})
    polarity_score: float = Field(..., json_schema_extra={"example": 0.2})
    emotions_detected: List[str] = Field(..., json_schema_extra={"example": ["Satisfaction", "Frustration"]})


class RecommendationRequest(BaseModel):
    customer_tier: str = Field(..., description="Customer subscription tier", json_schema_extra={"example": "Enterprise Gold"})
    account_age_months: int = Field(..., description="Tenure in months", json_schema_extra={"example": 24})
    ticket_subject: str = Field(..., description="Support issue subject", json_schema_extra={"example": "Downtime SLA breach credit request"})


class RecommendationResponse(BaseModel):
    action: str = Field(..., json_schema_extra={"example": "Issue $200 SLA Service Credit"})
    priority: str = Field(..., json_schema_extra={"example": "High"})
    explanation: str = Field(..., json_schema_extra={"example": "High-value enterprise customer with 24-month tenure eligible for automated SLA compensation."})
