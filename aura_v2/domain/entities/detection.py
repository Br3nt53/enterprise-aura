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
        _ = float(self.confidence)
