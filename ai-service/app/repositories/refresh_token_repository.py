from datetime import datetime
from typing import Optional, Dict, Any
from app.database.connection import db_connection
from app.core.config import settings
from app.core.logger import logger


class RefreshTokenRepository:
    """MongoDB persistence for refresh-token hashes and their revocation state."""

    def _collection(self):
        return db_connection.get_collection(settings.REFRESH_TOKEN_COLLECTION)

    async def create(self, token_hash: str, user_id: str, expires_at: Optional[str] = None) -> Dict[str, Any]:
        doc = {
            "tokenHash": token_hash,
            "userId": user_id,
            "createdAt": datetime.utcnow().isoformat(),
            "expiresAt": expires_at,
            "revoked": False,
        }
        col = self._collection()
        if col is not None:
            await col.insert_one(doc)
        return doc

    async def get_active_by_hash(self, token_hash: str) -> Optional[Dict[str, Any]]:
        col = self._collection()
        if col is not None:
            return await col.find_one({"tokenHash": token_hash, "revoked": False})
        return None

    async def revoke_by_hash(self, token_hash: str) -> bool:
        col = self._collection()
        if col is None:
            return False
        result = await col.update_one(
            {"tokenHash": token_hash},
            {"$set": {"revoked": True, "revokedAt": datetime.utcnow().isoformat()}},
        )
        return result.modified_count > 0

    async def revoke_all_for_user(self, user_id: str) -> int:
        col = self._collection()
        if col is None:
            return 0
        result = await col.update_many(
            {"userId": user_id, "revoked": False},
            {"$set": {"revoked": True, "revokedAt": datetime.utcnow().isoformat()}},
        )
        return result.modified_count

    async def delete_by_hash(self, token_hash: str) -> bool:
        col = self._collection()
        if col is None:
            return False
        result = await col.delete_one({"tokenHash": token_hash})
        return result.deleted_count > 0


refresh_token_repository = RefreshTokenRepository()
