from fastapi import APIRouter
from app.routers import chat, reasoning, sentiment, recommendation, analyze

api_v1_router = APIRouter()

# Register v1 sub-routers
api_v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_v1_router.include_router(reasoning.router, prefix="/reasoning", tags=["Reasoning"])
api_v1_router.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment"])
api_v1_router.include_router(recommendation.router, prefix="/recommendation", tags=["Recommendation"])
api_v1_router.include_router(analyze.router, prefix="/analyze", tags=["Analysis"])
