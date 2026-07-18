from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class UserRecord(BaseModel):
    """Schema for the persisted user document in MongoDB."""

    model_config = ConfigDict(extra="ignore")

    userId: str
    name: str
    email: str
    passwordHash: str
    role: str = "USER"
    status: str = "ACTIVE"
    createdAt: str
    updatedAt: str
    lastLogin: Optional[str] = None
    refreshTokenHashes: List[str] = Field(default_factory=list)
