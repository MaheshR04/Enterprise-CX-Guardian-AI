from datetime import datetime
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.database.connection import db_connection
from app.models.user import UserRecord
from app.utils.exceptions import MongoUnavailableException


class UserRepository:
    """MongoDB-backed repository for user accounts and refresh tokens."""

    def _collection(self):
        return db_connection.get_collection(settings.USER_COLLECTION)

    def _serialize(self, document: Optional[Dict[str, Any]]) -> Optional[UserRecord]:
        if not document:
            return None
        return UserRecord(**document)

    async def create(self, user: UserRecord) -> UserRecord:
        collection = self._collection()
        if collection is None:
            raise MongoUnavailableException("MongoDB is unavailable while creating the user account.")
        payload = user.model_dump()
        await collection.insert_one(payload)
        return user

    async def get_by_email(self, email: str) -> Optional[UserRecord]:
        collection = self._collection()
        if collection is None:
            raise MongoUnavailableException("MongoDB is unavailable while reading the user account.")
        document = await collection.find_one({"email": email.lower()})
        return self._serialize(document)

    async def get_by_user_id(self, user_id: str) -> Optional[UserRecord]:
        collection = self._collection()
        if collection is None:
            raise MongoUnavailableException("MongoDB is unavailable while reading the user account.")
        document = await collection.find_one({"userId": user_id})
        return self._serialize(document)

    async def email_exists(self, email: str) -> bool:
        collection = self._collection()
        if collection is None:
            raise MongoUnavailableException("MongoDB is unavailable while checking the email address.")
        document = await collection.find_one({"email": email.lower()})
        return document is not None

    async def add_refresh_token_hash(self, user_id: str, token_hash: str) -> None:
        collection = self._collection()
        if collection is None:
            raise MongoUnavailableException("MongoDB is unavailable while saving the refresh token.")
        await collection.update_one(
            {"userId": user_id},
            {"$addToSet": {"refreshTokenHashes": token_hash}}
        )

    async def remove_refresh_token_hash(self, user_id: str, token_hash: str) -> None:
        collection = self._collection()
        if collection is None:
            raise MongoUnavailableException("MongoDB is unavailable while removing the refresh token.")
        await collection.update_one(
            {"userId": user_id},
            {"$pull": {"refreshTokenHashes": token_hash}}
        )

    async def find_by_refresh_token_hash(self, token_hash: str) -> Optional[UserRecord]:
        collection = self._collection()
        if collection is None:
            raise MongoUnavailableException("MongoDB is unavailable while validating the refresh token.")
        document = await collection.find_one({"refreshTokenHashes": token_hash})
        return self._serialize(document)

    async def update_last_login(self, user_id: str) -> None:
        collection = self._collection()
        if collection is None:
            raise MongoUnavailableException("MongoDB is unavailable while updating the login timestamp.")
        await collection.update_one(
            {"userId": user_id},
            {"$set": {"lastLogin": datetime.utcnow().isoformat(), "updatedAt": datetime.utcnow().isoformat()}}
        )
