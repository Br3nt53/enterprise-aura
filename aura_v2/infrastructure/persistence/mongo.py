from __future__ import annotations
import os
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from ...domain.entities import Track

class MongoTrackRepository:
    def __init__(self) -> None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        db = os.getenv("MONGO_DB", "aura_db")
        coll = os.getenv("MONGO_COLLECTION", "tracks")
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=2000)
        self._collection: AsyncIOMotorCollection = client[db][coll]
        self._indexed = False

    async def _ensure_indexes(self) -> None:
        if self._indexed:
            return
        await self._collection.create_index("track_id", unique=True)
        self._indexed = True

    async def save(self, track: Track) -> None:
        await self._ensure_indexes()
        doc = track.to_dict()
        doc["track_id"] = track.id
        await self._collection.replace_one({"track_id": track.id}, doc, upsert=True)

    async def get(self, track_id: str) -> Optional[Track]:
        await self._ensure_indexes()
        doc = await self._collection.find_one({"track_id": track_id})
        return Track.from_dict(doc) if doc else None

    async def list(self) -> List[Track]:
        await self._ensure_indexes()
        docs = await self._collection.find({}).to_list(length=None)
        return [Track.from_dict(d) for d in docs]

    async def delete(self, track_id: str) -> None:
        await self._ensure_indexes()
        await self._collection.delete_one({"track_id": track_id})
