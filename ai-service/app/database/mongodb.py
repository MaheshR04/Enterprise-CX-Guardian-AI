from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.core.config import settings
from app.core.logger import logger

class DatabaseManager:
    """
    MongoDB Motor Async Connection Client Manager.
    Manages connection lifecycle and provides collection access handlers.
    """
    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect_to_mongo(cls):
        """
        Establishes connection to MongoDB Atlas / Local cluster via Motor async driver.
        """
        try:
            logger.info(f"[MongoDB Driver] Connecting to MongoDB instance at {settings.MONGODB_URI}...")
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            cls.db = cls.client[settings.DB_NAME]
            # Ping database server to verify connectivity
            await cls.client.admin.command('ping')
            logger.info(f"[MongoDB Driver] Successfully connected to database '{settings.DB_NAME}'")
        except Exception as err:
            logger.warning(f"[MongoDB Warning] Connection to MongoDB unavailable ({err}). Microservice operating in resilient mode.")
            cls.db = None

    @classmethod
    async def close_mongo_connection(cls):
        """
        Closes Motor MongoDB client connection gracefully.
        """
        if cls.client:
            cls.client.close()
            logger.info("[MongoDB Driver] Closed MongoDB connection pool")

    @classmethod
    def get_collection(cls, collection_name: str):
        """
        Retrieves a database collection handle.
        """
        if cls.db is not None:
            return cls.db[collection_name]
        return None

db_manager = DatabaseManager()
