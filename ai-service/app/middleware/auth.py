from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from app.schemas.auth import UserProfile
from app.services.auth_service import AuthService, auth_service


def get_auth_service() -> AuthService:
    return auth_service


async def get_current_user(
    authorization: Optional[str] = Header(default=None),
    service: AuthService = Depends(get_auth_service),
) -> UserProfile:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token is required")

    token = authorization.split(" ", 1)[1].strip()
    payload = service.decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Access token is required")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    profile_response = await service.get_user_profile(user_id)
    user = profile_response["user"]
    if user.status.upper() != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
    return user


def require_roles(*roles: str):
    async def dependency(current_user: UserProfile = Depends(get_current_user)) -> UserProfile:
        if current_user.role.upper() not in {role.upper() for role in roles}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
        return current_user

    return dependency
