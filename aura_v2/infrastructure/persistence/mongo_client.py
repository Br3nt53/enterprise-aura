from __future__ import annotations
import os
import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

class MongoProvider:
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    def init(cls) -> AsyncIOMotorDatabase:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        dbn = os.getenv("MONGO_DB", "aura")
        cls._client = AsyncIOMotorClient(uri, uuidRepresentation="standard")
        cls._db = cls._client[dbn]
        return cls._db

    @classmethod
    def db(cls) -> AsyncIOMotorDatabase:
        if cls._db is None:
            return cls.init()
        return cls._db

    @classmethod
    async def ping(cls) -> bool:
        db = cls.db()
        try:
            await db.command("ping")
            return True
        except Exception:
            return False

    @classmethod
    async def close(cls) -> None:
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None
