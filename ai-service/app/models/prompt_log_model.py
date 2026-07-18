from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class PromptLogModel(BaseModel):
    """
    MongoDB Prompt Log Document Model.

    Stored in: PROMPT_LOG_COLLECTION (default: "prompt_logs")

    Records the exact prompt payload sent to the Groq LLM for every AI completion
    request. Enables full prompt auditability, debugging, and replay capability.
    """

    prompt_id: str = Field(
        ...,
        alias="promptId",
        description="Unique UUID identifying this prompt log entry.",
        example="prompt_1a2b3c4d-1234-5678-abcd-ef0123456789"
    )
    conversation_id: str = Field(
        ...,
        alias="conversationId",
        description="Parent conversation session UUID this prompt belongs to.",
        example="conv_7a8b9c0d-1234-5678-abcd-ef0123456789"
    )
    system_prompt: str = Field(
        ...,
        alias="systemPrompt",
        description=(
            "The system-level instructions injected at the start of the LLM context window. "
            "Defines AI persona, tone, and behavioral constraints."
        ),
        example="You are an expert AI customer experience agent. Be helpful, concise, and professional."
    )
    user_prompt: str = Field(
        ...,
        alias="userPrompt",
        description=(
            "The formatted user turn including the sliding conversation history window. "
            "Assembled by PromptBuilder from prior messages and the current user message."
        ),
        example="Customer: Hello, what services do you offer?\nAI: I can help you with...\nCustomer: Tell me more."
    )
    final_prompt: str = Field(
        ...,
        alias="finalPrompt",
        description=(
            "The complete assembled LLM prompt payload transmitted to Groq. "
            "Combines systemPrompt + conversationHistory + currentUserMessage."
        ),
        example="System: You are an expert AI...\nCustomer: Hello\nAI: Hello!\nCustomer: Tell me more."
    )
    model: str = Field(
        ...,
        description="The Groq LLM model name used for this completion request.",
        example="llama3-70b-8192"
    )
    created_at: str = Field(
        ...,
        alias="createdAt",
        description="ISO 8601 timestamp when this prompt was assembled and dispatched.",
        example="2026-07-18T14:35:00.000000"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Optional extensible metadata (e.g., temperature, max_tokens, prompt_version)."
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "promptId": "prompt_1a2b3c4d-1234-5678-abcd-ef0123456789",
                "conversationId": "conv_7a8b9c0d-1234-5678-abcd-ef0123456789",
                "systemPrompt": "You are an expert AI customer experience agent.",
                "userPrompt": "Customer: Hello\nAI: Hello!\nCustomer: Tell me more.",
                "finalPrompt": "System: ...\nCustomer: Hello\nAI: Hello!\nCustomer: Tell me more.",
                "model": "llama3-70b-8192",
                "createdAt": "2026-07-18T14:35:00.000000"
            }
        }
