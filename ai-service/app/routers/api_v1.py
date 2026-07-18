from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user
from app.routers import auth, chat, conversation, reasoning, sentiment, recommendation, analyze

api_v1_router = APIRouter()

# Register v1 sub-routers
api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(chat.router, prefix="/chat", tags=["Chat"], dependencies=[Depends(get_current_user)])
api_v1_router.include_router(conversation.router, prefix="/conversations", tags=["Conversations"], dependencies=[Depends(get_current_user)])
api_v1_router.include_router(reasoning.router, prefix="/reasoning", tags=["Reasoning"], dependencies=[Depends(get_current_user)])
api_v1_router.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment"], dependencies=[Depends(get_current_user)])
api_v1_router.include_router(recommendation.router, prefix="/recommendation", tags=["Recommendation"], dependencies=[Depends(get_current_user)])
api_v1_router.include_router(analyze.router, prefix="/analyze", tags=["Analysis"], dependencies=[Depends(get_current_user)])
