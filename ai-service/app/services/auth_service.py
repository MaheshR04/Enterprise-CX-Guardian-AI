from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.logger import logger
from app.models.user import UserRecord
from app.repositories.refresh_token_repository import RefreshTokenRepository, refresh_token_repository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPair, UserProfile
from app.utils.exceptions import AuthenticationException, CustomValidationException, DuplicateUserException, NotFoundException


class AuthService:
    """Handles registration, login, token issuance, and RBAC checks."""

    def __init__(
        self,
        user_repo: Optional[UserRepository] = None,
        refresh_token_repo: Optional[RefreshTokenRepository] = None,
    ):
        self.user_repo = user_repo or UserRepository()
        self.refresh_token_repo = refresh_token_repo or refresh_token_repository
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.allowed_roles = {"ADMIN", "USER", "SUPPORT", "SUPER_ADMIN"}

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, payload: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = dict(payload)
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "access"})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def create_refresh_token(self, payload: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = dict(payload)
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"})
        return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_token(self, token: str) -> Dict[str, Any]:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except JWTError as exc:
            raise AuthenticationException("Invalid or expired token") from exc

    def _hash_token(self, token: str) -> str:
        return self.pwd_context.hash(token)

    def _to_profile(self, user: UserRecord) -> UserProfile:
        return UserProfile(
            userId=user.userId,
            name=user.name,
            email=user.email,
            role=user.role,
            status=user.status,
            createdAt=user.createdAt,
            updatedAt=user.updatedAt,
            lastLogin=user.lastLogin,
        )

    async def register_user(self, request_data: Any) -> Dict[str, Any]:
        normalized_email = request_data.email.lower()
        if await self.user_repo.email_exists(normalized_email):
            raise DuplicateUserException(normalized_email)

        role = str(request_data.role).upper()
        if role not in self.allowed_roles:
            raise CustomValidationException(message="Role is invalid", detail="Supported roles are ADMIN, USER, SUPPORT, and SUPER_ADMIN")

        now = datetime.utcnow().isoformat()
        user = UserRecord(
            userId=f"usr_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
            name=request_data.name.strip(),
            email=normalized_email,
            passwordHash=self.hash_password(request_data.password),
            role=role,
            status="ACTIVE",
            createdAt=now,
            updatedAt=now,
            lastLogin=None,
        )
        created_user = await self.user_repo.create(user)
        tokens = await self._issue_tokens_and_store(created_user)
        logger.info(f"[AuthService] Registered user '{created_user.userId}'")
        return {
            "message": "User registered successfully",
            "user": self._to_profile(created_user),
            "tokens": tokens,
        }

    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        user = await self.user_repo.get_by_email(email.lower())
        if not user:
            raise AuthenticationException("Invalid email or password")
        if not self.verify_password(password, user.passwordHash):
            raise AuthenticationException("Invalid email or password")
        if user.status.upper() != "ACTIVE":
            raise AuthenticationException("User account is inactive")

        await self.user_repo.update_last_login(user.userId)
        tokens = await self._issue_tokens_and_store(user)
        logger.info(f"[AuthService] User '{user.userId}' logged in")
        return {
            "message": "Login successful",
            "user": self._to_profile(user),
            "tokens": tokens,
        }

    async def refresh_user_token(self, refresh_token: str) -> Dict[str, Any]:
        payload = self.decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationException("Refresh token is invalid")

        token_hash = self._hash_token(refresh_token)
        active_token = await self.refresh_token_repo.get_active_by_hash(token_hash)
        if not active_token:
            raise AuthenticationException("Refresh token is invalid or expired")
        user = await self.user_repo.get_by_user_id(active_token["userId"])
        if not user:
            raise AuthenticationException("Refresh token is invalid or expired")
        if user.status.upper() != "ACTIVE":
            raise AuthenticationException("User account is inactive")

        await self.refresh_token_repo.revoke_by_hash(token_hash)
        refreshed_tokens = await self._issue_tokens_and_store(user)
        logger.info(f"[AuthService] Refreshed tokens for user '{user.userId}'")
        return {
            "message": "Token refreshed successfully",
            "user": self._to_profile(user),
            "tokens": refreshed_tokens,
        }

    async def logout_user(self, user_id: str, refresh_token: Optional[str] = None) -> Dict[str, Any]:
        if refresh_token:
            token_hash = self._hash_token(refresh_token)
            await self.refresh_token_repo.revoke_by_hash(token_hash)
        else:
            await self.refresh_token_repo.revoke_all_for_user(user_id)
        logger.info(f"[AuthService] Logged out user '{user_id}'")
        return {"message": "Logout successful"}

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        user = await self.user_repo.get_by_user_id(user_id)
        if not user:
            raise NotFoundException(message="User not found", detail="The requested user profile does not exist")
        return {"message": "Profile retrieved successfully", "user": self._to_profile(user)}

    def _issue_tokens(self, user: UserRecord) -> TokenPair:
        access_payload = {"sub": user.userId, "role": user.role}
        refresh_payload = {"sub": user.userId, "role": user.role}
        access_token = self.create_access_token(access_payload)
        refresh_token = self.create_refresh_token(refresh_payload)

        return TokenPair(
            accessToken=access_token,
            refreshToken=refresh_token,
            tokenType="bearer",
            expiresIn=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def _issue_tokens_and_store(self, user: UserRecord) -> TokenPair:
        token_pair = self._issue_tokens(user)
        token_hash = self._hash_token(token_pair.refreshToken)
        await self.user_repo.add_refresh_token_hash(user.userId, token_hash)
        await self.refresh_token_repo.create(token_hash, user.userId)
        return token_pair


auth_service = AuthService()
