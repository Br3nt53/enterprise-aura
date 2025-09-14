from __future__ import annotations
import abc
import asyncio
import datetime as dt
from typing import AsyncIterator, Dict, Any, Iterable

Detection = Dict[str, Any]


class DetectionSource(abc.ABC):
    @abc.abstractmethod
    async def frames(self) -> AsyncIterator[Dict[str, Any]]:
        """Yield TrackingRequest-shaped dicts."""


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def batch(
    camera: Iterable[Detection] = (),
    radar: Iterable[Detection] = (),
    lidar: Iterable[Detection] = (),
) -> Dict[str, Any]:
    return {
        "camera_detections": list(camera),
        "radar_detections": list(radar),
        "lidar_detections": list(lidar),
        "timestamp": now_iso(),
    }
