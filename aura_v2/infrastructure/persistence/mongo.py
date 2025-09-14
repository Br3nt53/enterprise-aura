from __future__ import annotations

import dataclasses
import os
from enum import Enum
from typing import Any, Dict, List, Mapping, Optional

try:
    import numpy as _np  # type: ignore
except Exception:  # pragma: no cover
    _np = None  # type: ignore

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)

from aura_v2.infrastructure.persistence.mongo_client import MongoProvider

try:
    from aura_v2.domain.entities import (
        Position3D,  # type: ignore[attr-defined]
        Track,  # type: ignore[attr-defined]
        TrackState,  # type: ignore[attr-defined]
        TrackStatus,  # type: ignore[attr-defined]
        Velocity3D,  # type: ignore[attr-defined]
    )
except Exception:  # noqa: BLE001
    from aura_v2.domain.entities.track import (  # type: ignore[no-redef]
        Position3D,
        Track,
        TrackState,
        TrackStatus,
        Velocity3D,
    )


def _is_dc_instance(o: Any) -> bool:
    return dataclasses.is_dataclass(o) and not isinstance(o, type)


def _jsonify(obj: Any) -> Any:
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if _np is not None and isinstance(obj, _np.generic):  # type: ignore[attr-defined]
        return obj.item()
    if isinstance(obj, Enum):
        return obj.value
    if _is_dc_instance(obj):
        return {k: _jsonify(v) for k, v in dataclasses.asdict(obj).items()}
    if hasattr(obj, "model_dump"):
        try:
            data = obj.model_dump(mode="python")  # type: ignore[attr-defined]
            return {k: _jsonify(v) for k, v in data.items()}
        except Exception:
            pass
    if hasattr(obj, "dict"):
        try:
            data = obj.dict()  # type: ignore[call-arg]
            return {k: _jsonify(v) for k, v in data.items()}
        except Exception:
            pass
    if isinstance(obj, Mapping):
        return {k: _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_jsonify(v) for v in obj]
    if hasattr(obj, "__dict__"):
        return {k: _jsonify(v) for k, v in vars(obj).items()}
    return str(obj)


def _reconstruct_state(data: Dict[str, Any]) -> None:
    st = data.get("state")
    if not isinstance(st, Mapping):
        return
    pos = st.get("position")
    vel = st.get("velocity")
    pos_obj = Position3D(**pos) if isinstance(pos, Mapping) else pos
    vel_obj = Velocity3D(**vel) if isinstance(vel, Mapping) and vel else None
    try:
        state_obj = TrackState(position=pos_obj, velocity=vel_obj)  # type: ignore[arg-type]
    except Exception:
        ks = {"position": pos_obj, "velocity": vel_obj}
        state_obj = TrackState(**{k: v for k, v in ks.items() if v is not None})  # type: ignore[call-arg]
    data["state"] = state_obj


def _reconstruct_enums(data: Dict[str, Any]) -> None:
    if "status" in data and not isinstance(data["status"], TrackStatus):
        try:
            data["status"] = TrackStatus(data["status"])
        except Exception:
            pass


class MongoTrackRepository:
    """Async repository for Track documents stored in collection 'tracks'."""

    collection_name = "tracks"

    def __init__(
        self,
        client: Optional[AsyncIOMotorClient] = None,
        db_name: Optional[str] = None,
        collection_name: Optional[str] = None,
    ) -> None:
        # Resolve client via provider, else env fallback
        if client is None:
            if hasattr(MongoProvider, "client"):
                client = MongoProvider.client()  # type: ignore[assignment]
            if client is None and hasattr(MongoProvider, "get_client"):
                client = MongoProvider.get_client()  # type: ignore[assignment]
            if client is None:
                env_uri = os.getenv(
                    "MONGO_URI",
                    "mongodb://root:example@mongo:27017/?authSource=admin&directConnection=true",
                )
                client = AsyncIOMotorClient(env_uri, serverSelectionTimeoutMS=5000)
        if client is None:
            raise RuntimeError("MongoProvider did not supply a client")
        self._client: AsyncIOMotorClient = client

        # Resolve database via provider, else env/default
        db: Optional[AsyncIOMotorDatabase] = None
        if hasattr(MongoProvider, "db"):
            try:
                db = MongoProvider.db()  # type: ignore[assignment]
            except Exception:
                db = None
        if db is None:
            name = db_name or os.getenv("MONGO_DB", "aura_test")
            db = self._client[name]
        self._db: AsyncIOMotorDatabase = db

        cname = collection_name or self.collection_name
        self._collection: AsyncIOMotorCollection = self._db[cname]

    @staticmethod
    def _to_doc(track: Any) -> Dict[str, Any]:
        if isinstance(track, dict):
            base: Dict[str, Any] = dict(track)
        elif hasattr(track, "model_dump"):
            base = track.model_dump(mode="python")  # type: ignore[attr-defined]
        elif hasattr(track, "dict"):
            base = track.dict()  # type: ignore[call-arg]
        else:
            base = vars(track)

        _id = base.get("id") or base.get("track_id") or base.get("_id")
        if not _id:
            raise ValueError("track must include one of: id, track_id, _id")
        base["_id"] = _id
        base.setdefault("id", _id)

        doc = _jsonify(base)
        doc["_id"] = str(_id)
        return doc  # type: ignore[return-value]

    @staticmethod
    def _to_track(doc: Mapping[str, Any]) -> Track:
        data: Dict[str, Any] = dict(doc)
        raw_id = str(data.pop("_id")) if "_id" in data else None
        if "id" not in data and raw_id is not None:
            data["id"] = raw_id
        _reconstruct_state(data)
        _reconstruct_enums(data)
        if hasattr(Track, "model_validate"):
            return Track.model_validate(data)  # type: ignore[attr-defined]
        return Track(**data)  # type: ignore[call-arg]

    async def save(self, track: Any) -> str:
        doc = self._to_doc(track)
        await self._collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        return str(doc["_id"])

    async def get_by_id(self, track_id: str) -> Optional[Track]:
        doc = await self._collection.find_one(
            {"$or": [{"_id": track_id}, {"id": track_id}, {"track_id": track_id}]}
        )
        return self._to_track(doc) if doc else None

    async def list(self) -> List[Track]:
        out: List[Track] = []
        async for d in self._collection.find({}):
            out.append(self._to_track(d))
        return out

    async def delete(self, track_id: str) -> int:
        res = await self._collection.delete_one({"_id": track_id})
        return int(res.deleted_count)

    async def delete_all(self) -> int:
        res = await self._collection.delete_many({})
        return int(res.deleted_count)
