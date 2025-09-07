from dataclasses import dataclass


@dataclass(frozen=True)
class Velocity2D:
    vx: float
    vy: float


@dataclass(frozen=True)
class Velocity3D(Velocity2D):
    vz: float
