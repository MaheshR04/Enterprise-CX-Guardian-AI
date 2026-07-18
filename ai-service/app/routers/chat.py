from fastapi import APIRouter, Depends, status
from typing import Optional
from app.schemas.payload import ChatRequest, DummyChatResponse, ErrorResponse
from app.services.groq_service import groq_service, GroqService
from app.utils.logger import logger

router = APIRouter()

def get_groq_service() -> GroqService:
    """Dependency injection provider for Groq SDK Client Service."""
    return groq_service

@router.post(
    "/",
    response_model=DummyChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Autonomous Chat Message Endpoint",
    description="Processes customer chat messages and returns an autonomous conversational agent response.",
    responses={
        200: {
            "model": DummyChatResponse,
            "description": "Chat response processed successfully."
        },
        422: {
            "model": ErrorResponse,
            "description": "Request validation failed due to invalid message payload structure."
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server processing error."
        }
    }
)
async def process_chat(
    payload: Optional[ChatRequest] = None,
    service: GroqService = Depends(get_groq_service)
) -> DummyChatResponse:
    """
    Asynchronously handles incoming chat interactions using injected Groq service dependencies.
    """
    logger.info("[Chat API] Processing POST /api/v1/chat request via injected GroqService")
    return DummyChatResponse(
        success=True,
        message="AI endpoint working",
        response="Hello from AI Service"
    )
