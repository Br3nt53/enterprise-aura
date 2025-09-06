# aura_v2/domain/value_objects/__init__.py
from .position import Position3D

# Define (or import) the rest as your codebase expects.
# If these live in their own modules, import them. If not, define them here.
# Example minimal shims that keep public API stable:

from pydantic import BaseModel
from typing import NewType, Tuple

TrackID = NewType("TrackID", int)
SensorID = NewType("SensorID", str)

class Covariance(BaseModel):
    # 3x3 covariance expressed as a flat 9-tuple (row-major) or however your code uses it
    matrix: Tuple[float, float, float, float, float, float, float, float, float]

class Velocity3D(BaseModel):
    vx: float
    vy: float
    vz: float

class Timestamp(BaseModel):
    # float seconds since epoch or monotonic time—match your usage
    t: float

__all__ = [
    "Position3D",
    "Velocity3D",
    "Covariance",
    "TrackID",
    "SensorID",
    "Timestamp",
]
