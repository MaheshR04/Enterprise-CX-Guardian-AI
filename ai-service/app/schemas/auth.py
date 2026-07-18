import re
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="USER")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", value):
            raise ValueError("Password must contain at least one special character")
        return value


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenRefreshRequest(BaseModel):
    refreshToken: str = Field(..., min_length=1)


class LogoutRequest(BaseModel):
    refreshToken: Optional[str] = None


class UserProfile(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    userId: str
    name: str
    email: str
    role: str
    status: str
    createdAt: str
    updatedAt: str
    lastLogin: Optional[str] = None


class TokenPair(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"
    expiresIn: int = 3600


class AuthResponse(BaseModel):
    message: str
    user: UserProfile
    tokens: TokenPair


class ProfileResponse(BaseModel):
    message: str
    user: UserProfile
