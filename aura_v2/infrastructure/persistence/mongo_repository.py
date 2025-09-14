from __future__ import annotations
import os
from typing import Any, Mapping, Optional, Dict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

class MongoTrackRepository:
    collection_name = "tracks"

    def __init__(self, client: AsyncIOMotorClient, db_name: Optional[str] = None) -> None:
        db_name = db_name or os.getenv("MONGO_DB", "aura_test")
        self._db = client[db_name]
        self._col: AsyncIOMotorCollection = self._db[self.collection_name]

    @staticmethod
    def _to_doc(track: Any) -> Dict[str, Any]:
        if isinstance(track, dict):
            doc = dict(track)
        elif hasattr(track, "model_dump"):
            doc = track.model_dump()
        elif hasattr(track, "dict"):
            doc = track.dict()
        else:
            doc = track.__dict__
        _id = doc.get("id") or doc.get("track_id") or doc.get("_id")
        if _id is None:
            raise ValueError("track must include one of: id, track_id, _id")
        doc["_id"] = _id
        doc.setdefault("id", _id)
        return doc

    async def save(self, track: Any) -> str:
        doc = self._to_doc(track)
        await self._col.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        return str(doc["_id"])

    async def get_by_id(self, track_id: str) -> Optional[Mapping[str, Any]]:
        doc = await self._col.find_one({"_id": track_id})
        if doc is not None and "id" not in doc and "_id" in doc:
            doc["id"] = doc["_id"]
        return doc

    async def delete_all(self) -> int:
        res = await self._col.delete_many({})
        return int(res.deleted_count)
