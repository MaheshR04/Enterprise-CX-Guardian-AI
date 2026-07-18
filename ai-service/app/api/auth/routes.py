from fastapi import APIRouter, Depends, status
from app.middleware.auth import get_auth_service, get_current_user
from app.schemas.auth import AuthResponse, LogoutRequest, ProfileResponse, TokenRefreshRequest, UserLoginRequest, UserProfile, UserRegisterRequest
from app.services.auth_service import AuthService

router = APIRouter()


def get_service() -> AuthService:
    return get_auth_service()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
async def register_user(payload: UserRegisterRequest, service: AuthService = Depends(get_service)) -> AuthResponse:
    result = await service.register_user(payload)
    return AuthResponse(message=result["message"], user=result["user"], tokens=result["tokens"])


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Log in and receive tokens",
)
async def login_user(payload: UserLoginRequest, service: AuthService = Depends(get_service)) -> AuthResponse:
    result = await service.login_user(payload.email, payload.password)
    return AuthResponse(message=result["message"], user=result["user"], tokens=result["tokens"])


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Refresh access and refresh tokens",
)
async def refresh_tokens(payload: TokenRefreshRequest, service: AuthService = Depends(get_service)) -> AuthResponse:
    result = await service.refresh_user_token(payload.refreshToken)
    return AuthResponse(message=result["message"], user=result["user"], tokens=result["tokens"])


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Invalidate the current refresh token",
)
async def logout_user(
    payload: LogoutRequest,
    current_user: UserProfile = Depends(get_current_user),
    service: AuthService = Depends(get_service),
):
    await service.logout_user(current_user.userId, payload.refreshToken)
    return {"message": "Logout successful"}


@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Get the current authenticated user's profile",
)
async def get_profile(current_user: UserProfile = Depends(get_current_user)) -> ProfileResponse:
    return ProfileResponse(message="Profile retrieved successfully", user=current_user)
