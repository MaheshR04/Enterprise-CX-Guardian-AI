from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AIUsageModel(BaseModel):
    """
    MongoDB AI Usage Telemetry Document Model.

    Stored in: AI_USAGE_COLLECTION (default: "ai_usage")

    Automatically persisted after every Groq LLM completion call.
    Records all 6 token usage metrics needed for cost tracking,
    performance monitoring, and future billing integration.
    """

    conversation_id: str = Field(
        ...,
        alias="conversationId",
        description="Parent conversation session UUID.",
        example="conv_7a8b9c0d-1234-5678-abcd-ef0123456789"
    )
    model: str = Field(
        ...,
        description="Groq LLM model name used for the completion request.",
        example="llama3-70b-8192"
    )
    prompt_tokens: int = Field(
        ...,
        alias="promptTokens",
        description="Number of tokens consumed in the assembled input prompt.",
        example=120
    )
    completion_tokens: int = Field(
        ...,
        alias="completionTokens",
        description="Number of tokens generated in the AI response.",
        example=80
    )
    total_tokens: int = Field(
        ...,
        alias="totalTokens",
        description="Combined total of promptTokens + completionTokens.",
        example=200
    )
    latency_ms: float = Field(
        ...,
        alias="latencyMs",
        description="Raw end-to-end Groq API response latency in milliseconds.",
        example=432.5
    )
    processing_time: str = Field(
        ...,
        alias="processingTime",
        description="Human-readable formatted latency string.",
        example="432ms"
    )
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp when the AI completion was received.",
        example="2026-07-18T14:35:00.000000"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional extensible metadata (e.g., temperature, fallback flag)."
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "conversationId": "conv_7a8b9c0d-1234-5678-abcd-ef0123456789",
                "model": "llama3-70b-8192",
                "promptTokens": 120,
                "completionTokens": 80,
                "totalTokens": 200,
                "latencyMs": 432.5,
                "processingTime": "432ms",
                "timestamp": "2026-07-18T14:35:00.000000"
            }
        }
