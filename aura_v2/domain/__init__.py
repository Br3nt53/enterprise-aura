"""
AURA v2 domain package.

This package aggregates the core domain abstractions used by the system:
value objects such as positions and velocities, entities like detections and
tracks, enumerations for statuses and threat levels, and service interfaces
for sensor fusion.  Importing from this package ensures that callers
receive the canonical definitions rather than ad‑hoc duplicates scattered
through the codebase.
"""

from .value_objects import Position3D, Velocity3D, Confidence
from .entities.detection import Detection
from .entities.track import (
    Track,
    TrackState,
    TrackStatus,
    ThreatLevel,
)

__all__ = [
    "Position3D",
    "Velocity3D",
    "Confidence",
    "Detection",
    "Track",
    "TrackState",
    "TrackStatus",
    "ThreatLevel",
]
