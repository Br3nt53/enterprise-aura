from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
from datetime import datetime

def _now() -> datetime:
    return _now(datetime.timezone.utc)
#
@dataclass
class Detection:
    ts: datetime
    sensor: str
    bbox: List[float]  # [x, y, w, h]
    score: float
    meta: Dict[str, Any]

    def to_bson(self) -> Dict[str, Any]:
        d = asdict(self)
        d["ts"] = self.ts
        return d

@dataclass
class TrackEvent:
    ts: datetime
    track_id: str
    assoc: Optional[Dict[str, Any]] = None  # association details (Hungarian)
    fused: Optional[Dict[str, Any]] = None  # UFK fused state
    state: Optional[Dict[str, Any]] = None  # kinematic state, etc.

    def to_bson(self) -> Dict[str, Any]:
        d = asdict(self)
        d["ts"] = self.ts
        return d

@dataclass
class MetricPoint:
    ts: datetime
    name: str
    value: float
    labels: Dict[str, str]

    def to_bson(self) -> Dict[str, Any]:
        d = asdict(self)
        d["ts"] = self.ts
        return d

@dataclass
class AuditLog:
    ts: datetime
    actor: str
    action: str
    detail: Dict[str, Any]

    def to_bson(self) -> Dict[str, Any]:
        d = asdict(self)
        d["ts"] = self.ts
        return d
