from __future__ import annotations

import numpy as np


def cv_transition(x: np.ndarray, dt: float) -> np.ndarray:
    # x = [x, y, vx, vy]^T
    xp = x.copy()
    xp[0, 0] += x[2, 0] * dt
    xp[1, 0] += x[3, 0] * dt
    return xp


def position_measurement(x: np.ndarray) -> np.ndarray:
    return x[0:2, :]
