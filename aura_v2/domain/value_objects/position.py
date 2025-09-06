from __future__ import annotations
from pydantic import BaseModel, Field
# aura_v2/domain/value_objects/position.py
from typing import Tuple

class Position3D(BaseModel):
    x: float
    y: float
    z: float

    def distance_to(self, other: "Position3D") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return (dx*dx + dy*dy + dz*dz) ** 0.5


class Position2D(BaseModel):
    x: float = Field(..., description="X coordinate (meters)")
    y: float = Field(..., description="Y coordinate (meters)")

class Position3D(BaseModel):
    x: float = Field(..., description="X coordinate (meters)")
    y: float = Field(..., description="Y coordinate (meters)")
    z: float = Field(..., description="Z coordinate (meters)")

class Velocity2D(BaseModel):
    vx: float = Field(..., description="Velocity along X (m/s)")
    vy: float = Field(..., description="Velocity along Y (m/s)")

class Velocity3D(BaseModel):
    vx: float = Field(..., description="Velocity along X (m/s)")
    vy: float = Field(..., description="Velocity along Y (m/s)")
    vz: float = Field(..., description="Velocity along Z (m/s)")
