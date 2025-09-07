"""
Domain detection entity.

Represents a single observation from a sensor at a specific time.  Each
detection carries a position in 3D space, an associated confidence and
sensor identifier, along with arbitrary attribute metadata.  Detections
are immutable to guarantee referential transparency during tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from ..value_objects import Position3D, Confidence

@dataclass(frozen=True, slots=True)
class Detection:
    timestamp: datetime
    position: Position3D
    confidence: Confidence
    sensor_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Validate confidence via Confidence.__post_init__
        _ = float(self.confidence)
