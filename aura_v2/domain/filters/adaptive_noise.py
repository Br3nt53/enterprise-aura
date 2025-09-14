from __future__ import annotations

from collections import deque

import numpy as np


class InnovationTracker:
    def __init__(self, maxlen: int = 50):
        self.buffer = deque(maxlen=maxlen)

    def update(self, innovation: np.ndarray):
        self.buffer.append(innovation)

    def covariance(self):
        if not self.buffer:
            return None
        arr = np.hstack(self.buffer)
        mean = arr.mean(axis=1, keepdims=True)
        diffs = arr - mean
        return (diffs @ diffs.T) / arr.shape[1]


def adapt_measurement_noise(
    R_current: np.ndarray, innovation_cov: np.ndarray, rho: float = 0.95
):
    if innovation_cov is None:
        return R_current
    return rho * R_current + (1 - rho) * innovation_cov
