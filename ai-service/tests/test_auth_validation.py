import asyncio
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.auth import UserRegisterRequest
from app.services.auth_service import AuthService


class DummyUserRepo:
    def __init__(self):
        self.created_user = None
        self.refresh_hashes = []

    async def email_exists(self, email: str) -> bool:
        return False

    async def create(self, user):
        self.created_user = user
        return user

    async def add_refresh_token_hash(self, user_id: str, token_hash: str) -> None:
        self.refresh_hashes.append((user_id, token_hash))

    async def update_last_login(self, user_id: str) -> None:
        return None

    async def get_by_email(self, email: str):
        return None

    async def get_by_user_id(self, user_id: str):
        return self.created_user if self.created_user and self.created_user.userId == user_id else None


class DummyRefreshTokenRepo:
    def __init__(self):
        self.created_tokens = []

    async def create(self, token_hash: str, user_id: str):
        self.created_tokens.append((token_hash, user_id))

    async def get_active_by_hash(self, token_hash: str):
        return None

    async def revoke_by_hash(self, token_hash: str) -> bool:
        return True

    async def revoke_all_for_user(self, user_id: str) -> int:
        return 0


def test_register_request_rejects_weak_password() -> None:
    with pytest.raises(ValidationError):
        UserRegisterRequest(
            name="Jane Doe",
            email="jane@example.com",
            password="weak",
            role="USER",
        )


def test_register_user_issues_tokens_and_persists_refresh_hash() -> None:
    async def run_test() -> None:
        user_repo = DummyUserRepo()
        refresh_repo = DummyRefreshTokenRepo()
        service = AuthService(user_repo=user_repo, refresh_token_repo=refresh_repo)
        request = SimpleNamespace(
            name="Jane Doe",
            email="jane@example.com",
            password="StrongPass123!",
            role="USER",
        )

        result = await service.register_user(request)

        assert result["tokens"].accessToken
        assert result["tokens"].refreshToken
        assert len(refresh_repo.created_tokens) == 1
        assert user_repo.refresh_hashes

    asyncio.run(run_test())
