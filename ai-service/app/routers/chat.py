from fastapi import APIRouter, Depends, status
from typing import Optional
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponsePayload, ChatResponseData, TokenUsage
from app.schemas.payload import ErrorResponse
from app.services.ai_service import ai_service, AIServiceManager
from app.utils.exceptions import CustomValidationException, InvalidConversationIdException
from app.core.config import settings
from app.core.logger import logger

router = APIRouter()

def get_ai_service() -> AIServiceManager:
    """Dependency injection provider for AI Service Manager."""
    return ai_service

@router.post(
    "/",
    response_model=ChatResponsePayload,
    status_code=status.HTTP_200_OK,
    summary="Chat Microservice Endpoint",
    description="Accepts chat input messages, loads system prompts, executes Groq LLM completions, and returns a standardized response.",
    responses={
        200: {
            "model": ChatResponsePayload,
            "description": "Response generated successfully."
        },
        400: {
            "model": ErrorResponse,
            "description": "Empty message or invalid conversation ID."
        },
        422: {
            "model": ErrorResponse,
            "description": "Request validation failed."
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error."
        }
    }
)
async def process_chat(
    payload: Optional[ChatRequest] = None,
    service: AIServiceManager = Depends(get_ai_service)
) -> ChatResponsePayload:
    """
    Asynchronously processes incoming chat requests via injected AIServiceManager.
    Performs empty message & conversation ID validation checks.
    """
    if not payload or not payload.message or not payload.message.strip():
        raise CustomValidationException(
            message="Empty Message Error",
            detail="Message content cannot be blank or empty whitespace."
        )

    msg = payload.message.strip()
    conv_id = (payload.conversationId or payload.conversation_id)
    temp = payload.temperature

    if conv_id and len(conv_id) > 128:
        raise InvalidConversationIdException(detail="Conversation ID exceeds maximum length threshold of 128 characters.")
    
    logger.info(f"[Chat API] Processing POST /api/v1/chat message: '{msg}' (temperature: {temp})")

    result = await service.process_message(
        message=msg,
        conversation_id=conv_id,
        temperature=temp
    )

    usage_data = result.get("usage", {})
    usage_model = TokenUsage(
        prompt_tokens=usage_data.get("prompt_tokens", 0),
        completion_tokens=usage_data.get("completion_tokens", 0),
        total_tokens=usage_data.get("total_tokens", 0)
    )

    return ChatResponsePayload(
        success=True,
        message="Response generated successfully",
        data=ChatResponseData(
            conversationId=result.get("conversation_id", "conv_default_001"),
            messageId=result.get("message_id", "msg_default_001"),
            reply=result.get("reply", "Hello from Groq LLaMA-3"),
            processingTime=result.get("processingTime", "15ms"),
            model=result.get("model", settings.MODEL_NAME),
            historyLength=result.get("historyLength", 2),
            usage=usage_model
        )
    )
