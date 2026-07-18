from fastapi import APIRouter, Depends, status
from app.schemas.payload import RecommendationRequest, RecommendationResponse, ErrorResponse
from app.recommendations.recommendation_engine import recommendation_engine, RecommendationEngine
from app.utils.logger import logger

router = APIRouter()

def get_recommendation_engine() -> RecommendationEngine:
    """Dependency injection provider for Next-Best-Action Recommendation Engine."""
    return recommendation_engine

@router.post(
    "/",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Next Best Action Recommendation Endpoint",
    description="Predicts optimal next-best-action recommendations based on customer account tier and ticket history.",
    responses={
        200: {
            "model": RecommendationResponse,
            "description": "Recommendation generated successfully."
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
async def predict_recommendation(
    payload: RecommendationRequest,
    engine: RecommendationEngine = Depends(get_recommendation_engine)
) -> RecommendationResponse:
    """
    Asynchronously generates next-best-action recommendations via injected RecommendationEngine.
    """
    logger.info(f"[Recommendation API] Generating action for customer tier: {payload.customer_tier}")
    result = await engine.get_recommendation({"customer_tier": payload.customer_tier})
    
    return RecommendationResponse(
        action=result.get("recommended_action", "Issue $100 Service Credit and Apology Email"),
        priority="High",
        explanation=f"Customer tier '{payload.customer_tier}' with {payload.account_age_months} months tenure qualifies for automated SLA compensation."
    )
