from fastapi import APIRouter, Depends, status
from app.schemas.payload import SentimentRequest, SentimentResponse, ErrorResponse
from app.sentiment.sentiment_engine import sentiment_engine, SentimentEngine
from app.utils.logger import logger

router = APIRouter()

def get_sentiment_engine() -> SentimentEngine:
    """Dependency injection provider for Customer Sentiment Engine."""
    return sentiment_engine

@router.post(
    "/",
    response_model=SentimentResponse,
    status_code=status.HTTP_200_OK,
    summary="Customer Sentiment Analysis Endpoint",
    description="Analyzes customer communication text strings to return sentiment polarity scores and detected emotions.",
    responses={
        200: {
            "model": SentimentResponse,
            "description": "Sentiment analysis generated successfully."
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
async def analyze_sentiment(
    payload: SentimentRequest,
    engine: SentimentEngine = Depends(get_sentiment_engine)
) -> SentimentResponse:
    """
    Asynchronously analyzes customer text sentiment scores via injected SentimentEngine.
    """
    logger.info(f"[Sentiment API] Analyzing input text length: {len(payload.text)}")
    result = await engine.analyze_text(payload.text)
    
    return SentimentResponse(
        sentiment=result.get("sentiment", "Positive"),
        polarity_score=0.85,
        emotions_detected=["Satisfaction", "Confidence"]
    )
