from dataclasses import dataclass


@dataclass(frozen=True)
class Position2D:
    x: float
    y: float


@dataclass(frozen=True)
class Position3D(Position2D):
    z: float
