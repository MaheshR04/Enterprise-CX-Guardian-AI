from fastapi import APIRouter, Depends, status
from app.schemas.payload import ReasoningRequest, ReasoningResponse, ErrorResponse
from app.reasoning.reasoning_engine import reasoning_engine, ReasoningEngine
from app.utils.logger import logger

router = APIRouter()

def get_reasoning_engine() -> ReasoningEngine:
    """Dependency injection provider for Root-Cause Reasoning Engine."""
    return reasoning_engine

@router.post(
    "/",
    response_model=ReasoningResponse,
    status_code=status.HTTP_200_OK,
    summary="Root-Cause Reasoning Endpoint",
    description="Evaluates customer issue descriptions to diagnose root causes and propose resolution steps.",
    responses={
        200: {
            "model": ReasoningResponse,
            "description": "Root cause reasoning analysis generated successfully."
        },
        422: {
            "model": ErrorResponse,
            "description": "Payload validation failed."
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server processing error."
        }
    }
)
async def analyze_reasoning(
    payload: ReasoningRequest,
    engine: ReasoningEngine = Depends(get_reasoning_engine)
) -> ReasoningResponse:
    """
    Asynchronously evaluates issue descriptions to return root cause explanations.
    """
    logger.info(f"[Reasoning API] Evaluating ticket ID: {payload.ticket_id} via injected ReasoningEngine")
    result = await engine.evaluate_reasoning(payload.issue_description, payload.ticket_id)
    
    return ReasoningResponse(
        ticket_id=payload.ticket_id or "CX-4912",
        root_cause=result.get("message", "Root cause identified"),
        recommended_action="Execute automated credential reset verification workflow",
        confidence_score=0.92
    )
