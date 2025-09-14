from __future__ import annotations
import os
from typing import Dict
from .mongo_client import MongoProvider

COLLECTION_TTLS: Dict[str, int] = {
    "tracks": int(os.getenv("TTL_TRACKS_H", "168")),
    "detections": int(os.getenv("TTL_DETECTIONS_H", "72")),
    "metrics": int(os.getenv("TTL_METRICS_H", "336")),
    "audit": int(os.getenv("TTL_AUDIT_H", "720")),
}

async def ensure_ttls() -> None:
    """Create/update TTL indexes on time fields."""
    db = MongoProvider.db()
    specs = {
        "tracks": ("ts", COLLECTION_TTLS["tracks"]),
        "detections": ("ts", COLLECTION_TTLS["detections"]),
        "metrics": ("ts", COLLECTION_TTLS["metrics"]),
        "audit": ("ts", COLLECTION_TTLS["audit"]),
    }
    for coll, (field, hours) in specs.items():
        expire_after = hours * 3600
        try:
            await db[coll].create_index(
                [(field, 1)],
                expireAfterSeconds=expire_after,
                name=f"ttl_{field}_{expire_after}",
                background=True,
            )
        except Exception:
            # best-effort; surfaced via health
            pass
