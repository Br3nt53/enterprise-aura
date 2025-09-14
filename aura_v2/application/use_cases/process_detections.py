# aura_v2/application/use_cases/process_detections.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

# ✅ Only depend on domain
from ...domain.entities import Detection
from ...domain.value_objects.confidence import Confidence
from ...domain.value_objects.position import Position3D


def _to_detection(d: Dict[str, Any]) -> Detection:
    """Normalize a loose sensor dict into a Detection entity."""
    ts = d.get("timestamp") or datetime.now(timezone.utc)
    x = float(d.get("x", 0.0))
    y = float(d.get("y", 0.0))
    z = float(d.get("z", 0.0))
    conf = float(d.get("confidence", 1.0))
    sensor_id = str(d.get("sensor_id", "unknown"))
    attrs = {
        k: v
        for k, v in d.items()
        if k not in {"timestamp", "x", "y", "z", "confidence", "sensor_id"}
    }
    return Detection(
        timestamp=ts,
        position=Position3D(x=x, y=y, z=z),
        confidence=Confidence(conf),
        sensor_id=sensor_id,
        attributes=attrs,
    )


class ProcessDetectionsUseCase:
    """
    Thin façade the tests treat as the 'pipeline'.

    We accept a runtime `tracker` that implements:
      `await tracker.update(detections, ts)` -> object with `.active_tracks`.
    """

    def __init__(self, tracker: Any, **_: Any) -> None:
        self.tracker = tracker

    async def __call__(
        self, sensor_data: Iterable[Dict[str, Any]], ts: Optional[datetime] = None
    ) -> Any:
        detections = [_to_detection(d) for d in sensor_data]
        ts = ts or datetime.now(timezone.utc)
        return await self.tracker.update(detections, ts)

    # ✅ Tests call `.process(...)` and expect a list[Track]
    async def process(self, sensor_data: Iterable[Dict[str, Any]], ts: Optional[datetime] = None):
        result = await self(sensor_data, ts)
        if hasattr(result, "active_tracks"):
            return list(getattr(result, "active_tracks"))
        if isinstance(result, list):
            return result
        return []
