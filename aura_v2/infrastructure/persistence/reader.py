from __future__ import annotations

from datetime import datetime
from typing import Any, AsyncIterator, Dict, Optional

from .mongo_client import MongoProvider


async def iter_tracks(
    since: Optional[datetime] = None,
) -> AsyncIterator[Dict[str, Any]]:
    query = {"ts": {"$gte": since}} if since else {}
    cursor = MongoProvider.db()["tracks"].find(query).sort("ts", 1).batch_size(500)
    async for doc in cursor:
        yield doc


async def latest_metrics(name: str, limit: int = 100) -> AsyncIterator[Dict[str, Any]]:
    cursor = MongoProvider.db()["metrics"].find({"name": name}).sort("ts", -1).limit(limit)
    async for doc in cursor:
        yield doc
