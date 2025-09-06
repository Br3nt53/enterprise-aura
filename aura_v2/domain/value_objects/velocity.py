from pydantic import BaseModel

class Velocity3D(BaseModel):
    """3D velocity (m/s)."""
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0
