from __future__ import annotations

from typing import Any, Dict

from .mongo_client import MongoProvider
from .schemas import AuditLog, Detection, MetricPoint, TrackEvent


class MongoWriter:
    @staticmethod
    async def write_detection(doc: Detection) -> None:
        await MongoProvider.db()["detections"].insert_one(doc.to_bson())

    @staticmethod
    async def write_track_event(doc: TrackEvent) -> None:
        await MongoProvider.db()["tracks"].insert_one(doc.to_bson())

    @staticmethod
    async def write_metric(doc: MetricPoint) -> None:
        await MongoProvider.db()["metrics"].insert_one(doc.to_bson())

    @staticmethod
    async def write_audit(doc: AuditLog) -> None:
        await MongoProvider.db()["audit"].insert_one(doc.to_bson())

    @staticmethod
    async def health() -> Dict[str, Any]:
        ok = await MongoProvider.ping()
        return {"mongo": "ok" if ok else "down"}
