# aura_v2/domain/entities/detection.py
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..value_objects import Confidence, CovarianceMatrix, Position3D, Velocity3D


@dataclass(frozen=True)
class Detection:
    """Represents a single sensor detection at a point in time."""

    sensor_id: str
    timestamp: datetime
    position: Position3D
    confidence: Confidence
    velocity: Optional[Velocity3D] = None
    covariance: Optional[CovarianceMatrix] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Detection":
        """Creates a Detection object from a dictionary."""
        pos = Position3D(
            x=data.get("x", data.get("position", {}).get("x", 0.0)),
            y=data.get("y", data.get("position", {}).get("y", 0.0)),
            z=data.get("z", data.get("position", {}).get("z", 0.0)),
        )

        # Handle different timestamp formats (float or string)
        ts_data = data.get("timestamp")
        if isinstance(ts_data, (int, float)):
            timestamp = datetime.fromtimestamp(ts_data, tz=timezone.utc)
        elif isinstance(ts_data, str):
            timestamp = datetime.fromisoformat(ts_data.replace("Z", "+00:00"))
        else:
            timestamp = datetime.now(timezone.utc)

        return cls(
            sensor_id=data.get("sensor_id", "unknown"),
            timestamp=timestamp,
            position=pos,
            confidence=Confidence(data.get("confidence", 0.5)),
            attributes=data.get("attributes", {}),
        )
