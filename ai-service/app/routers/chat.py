from fastapi import APIRouter, Depends, status
from typing import Optional
from app.middleware.auth import get_current_user
from app.schemas.auth import UserProfile
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponsePayload, ChatResponseData, TokenUsage
from app.schemas.payload import ErrorResponse
from app.services.ai_service import ai_service, AIServiceManager
from app.utils.exceptions import CustomValidationException, InvalidConversationIdException
from app.core.config import settings
from app.core.logger import logger

router = APIRouter()


def get_ai_service() -> AIServiceManager:
    """Dependency injection provider for AIServiceManager."""
    return ai_service


# ======================================================================
# POST /api/v1/chat
# ======================================================================
@router.post(
    "/",
    response_model=ChatResponsePayload,
    status_code=status.HTTP_200_OK,
    tags=["Chat"],
    summary="Send a Chat Message",
    description=(
        "Accepts a user message and runs the **10-step MongoDB-backed Chat Flow**:\n\n"
        "1. Receive request\n"
        "2. Create conversation in MongoDB (if new)\n"
        "3. Save user message → `MESSAGE_COLLECTION`\n"
        "4. Load conversation history from MongoDB\n"
        "5. Build prompt (system + history + message)\n"
        "6. Send to Groq (`llama3-70b-8192`)\n"
        "7. Receive AI response\n"
        "8. Save assistant response → `MESSAGE_COLLECTION`\n"
        "9. Save token usage → `AI_USAGE_COLLECTION` + prompt log → `PROMPT_LOG_COLLECTION`\n"
        "10. Return standardised response\n"
    ),
    responses={
        200: {
            "description": "AI response generated successfully.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Response generated successfully",
                        "data": {
                            "conversationId":  "conv_7a8b9c0d-1234-5678-abcd-ef0123456789",
                            "messageId":       "msg_8f1b2c3d-5678-1234-efab-cd0123456789",
                            "reply":           "Hello! I'm your AI customer experience agent. How can I assist you today?",
                            "processingTime":  "432ms",
                            "model":           "llama3-70b-8192",
                            "historyLength":   2,
                            "usage": {
                                "prompt_tokens":     120,
                                "completion_tokens":  80,
                                "total_tokens":      200
                            }
                        }
                    }
                }
            }
        },
        400: {
            "description": "Empty message or invalid conversation ID.",
            "content": {
                "application/json": {
                    "example": {
                        "success":    False,
                        "message":   "Empty Message",
                        "error":     "Message content cannot be blank or empty whitespace.",
                        "error_code": "EMPTY_MESSAGE"
                    }
                }
            }
        },
        422: {
            "description": "Request body validation failed.",
            "content": {
                "application/json": {
                    "example": {
                        "success":    False,
                        "message":   "Request Validation Failed",
                        "error":     "body → message: field required",
                        "error_code": "VALIDATION_ERROR"
                    }
                }
            }
        },
        503: {
            "description": "MongoDB unavailable — operating in fallback mode.",
            "content": {
                "application/json": {
                    "example": {
                        "success":    False,
                        "message":   "Database Unavailable",
                        "error":     "MongoDB is currently unavailable.",
                        "error_code": "DB_UNAVAILABLE"
                    }
                }
            }
        },
        502: {
            "description": "Groq LLM service error.",
            "content": {
                "application/json": {
                    "example": {
                        "success":    False,
                        "message":   "LLM Service Error",
                        "error":     "Groq API returned an unexpected error.",
                        "error_code": "LLM_SERVICE_ERROR"
                    }
                }
            }
        }
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "new_conversation": {
                            "summary": "Start a new conversation",
                            "value":   {"message": "Hello, how can you help me today?"}
                        },
                        "continue_conversation": {
                            "summary": "Continue an existing conversation",
                            "value":   {
                                "message":        "Can you tell me more about your pricing plans?",
                                "conversationId": "conv_7a8b9c0d-1234-5678-abcd-ef0123456789"
                            }
                        },
                        "with_temperature": {
                            "summary": "Custom temperature setting",
                            "value":   {
                                "message":     "Write a creative description of our product.",
                                "temperature": 0.8
                            }
                        }
                    }
                }
            }
        }
    }
)
async def process_chat(
    payload: Optional[ChatRequest] = None,
    current_user: UserProfile = Depends(get_current_user),
    service: AIServiceManager = Depends(get_ai_service)
) -> ChatResponsePayload:
    """
    Executes the 10-step MongoDB-backed Chat Flow:
    Receive → Create Conversation → Save User Message → Load History →
    Build Prompt → Send to Groq → Receive Response → Save Assistant Message →
    Save Token Usage + Prompt Log → Return Response.
    """
    # Validate message is not empty
    if not payload or not payload.message or not payload.message.strip():
        raise CustomValidationException(
            message="Empty Message",
            detail="Message content cannot be blank or empty whitespace."
        )

    msg     = payload.message.strip()
    conv_id = getattr(payload, "conversationId", None) or getattr(payload, "conversation_id", None)
    temp    = getattr(payload, "temperature", None)

    # Validate conversation ID length
    if conv_id and len(conv_id) > 128:
        raise InvalidConversationIdException(
            detail="Conversation ID must be a non-empty string under 128 characters."
        )

    logger.info(
        f"[Chat Router] POST /api/v1/chat | "
        f"ConvID: {conv_id or 'new'} | Temp: {temp}"
    )

    # Delegate to AIServiceManager — full 10-step Chat Flow
    result = await service.process_message(
        message=msg,
        conversation_id=conv_id,
        temperature=temp,
        user_id=current_user.userId
    )

    # Build token usage model
    usage_data  = result.get("usage", {})
    usage_model = TokenUsage(
        prompt_tokens=usage_data.get("prompt_tokens", 0),
        completion_tokens=usage_data.get("completion_tokens", 0),
        total_tokens=usage_data.get("total_tokens", 0)
    )

    return ChatResponsePayload(
        success=True,
        message="Response generated successfully",
        data=ChatResponseData(
            conversationId=result.get("conversation_id", "conv_default"),
            messageId=result.get("message_id", "msg_default"),
            reply=result.get("reply", ""),
            processingTime=result.get("processingTime", "15ms"),
            model=result.get("model", settings.MODEL_NAME),
            historyLength=result.get("historyLength", 0),
            usage=usage_model
        )
    )
