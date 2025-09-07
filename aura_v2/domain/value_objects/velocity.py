from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True, slots=True)
class Velocity3D:
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0

    @property
    def magnitude(self) -> float:
        return float((self.vx*self.vx + self.vy*self.vy + self.vz*self.vz) ** 0.5)

    def to_array(self) -> np.ndarray:
        return np.array([self.vx, self.vy, self.vz], dtype=float)
