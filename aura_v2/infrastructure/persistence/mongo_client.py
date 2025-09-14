# aura_v2/infrastructure/persistence/mongo_client.py
from __future__ import annotations

import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoProvider:
    """Global async Mongo provider used by tests and repositories."""

    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    _db_name: Optional[str] = None

    @classmethod
    def init(cls, uri: str | None = None, db_name: str | None = None) -> None:
        """Initialize client and db from args or env."""
        uri = uri or os.getenv(
            "MONGO_URI",
            "mongodb://root:example@mongo:27017/?authSource=admin&directConnection=true",
        )
        cls._db_name = db_name or os.getenv("MONGO_DB", "aura_test")
        cls._client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        cls._db = cls._client[cls._db_name]

    @classmethod
    def client(cls) -> Optional[AsyncIOMotorClient]:
        return cls._client

    @classmethod
    def get_client(cls) -> Optional[AsyncIOMotorClient]:
        return cls._client  # back-compat alias

    @classmethod
    def db(cls) -> Optional[AsyncIOMotorDatabase]:
        return cls._db

    @classmethod
    async def _ttl_present(cls) -> bool:
        """Robust TTL probe using index_information() to avoid cursor races."""
        if cls._db is None:
            return False
        try:
            info = await cls._db["tracks"].index_information()
            for _, spec in info.items():
                if "expireAfterSeconds" in spec:
                    return True
        except Exception:
            return False
        return False

    @classmethod
    async def ensure_ttl(cls) -> None:
        """Ensure a TTL index exists on tracks.updated_at."""
        if cls._db is None:
            cls.init()
        assert cls._db is not None
        ttl_seconds = int(os.getenv("AURA_TTL_SECONDS", "3600"))
        try:
            await cls._db["tracks"].create_index(
                "updated_at", expireAfterSeconds=ttl_seconds
            )
        except Exception:
            # Non-fatal if index exists or cannot be created due to perms
            pass

    @classmethod
    async def ping(cls, timeout: float = 30.0) -> bool:
        """
        Awaitable readiness probe.
        Succeeds only after server responds to ping AND a TTL index is present.
        Self-heals if the DB was dropped between tests.
        """
        import asyncio

        if cls._client is None or cls._db is None:
            cls.init()

        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        last_err: Optional[BaseException] = None

        while True:
            try:
                # Re-init if a previous test closed/dropped the client/DB.
                if cls._client is None or cls._db is None:
                    cls.init()

                assert cls._client is not None
                await cls._client.admin.command("ping")

                # Create TTL if missing, then confirm presence.
                await cls.ensure_ttl()
                if await cls._ttl_present():
                    return True
            except Exception as e:
                # If the database was dropped mid-flight, re-init and retry.
                last_err = e
                cls.init()

            if loop.time() >= deadline:
                if last_err:
                    raise last_err
                raise TimeoutError("TTL index not ready")

            await asyncio.sleep(0.2)

    @classmethod
    async def close(cls) -> None:
        """Awaitable close for tests that await this method."""
        if cls._client is not None:
            cls._client.close()
        cls._client = None
        cls._db = None
        cls._db_name = None
