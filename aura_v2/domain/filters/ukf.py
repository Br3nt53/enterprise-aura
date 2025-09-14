from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np


@dataclass
class UKFConfig:
    dt: float = 0.1
    alpha: float = 1e-3
    beta: float = 2.0
    kappa: float = 0.0
    process_var: float = 1.0
    meas_var_pos: float = 0.5


class UKF:
    def __init__(self, config: UKFConfig):
        self.cfg = config
        # State: [x, y, vx, vy]
        self.n = 4
        self.x = np.zeros((self.n, 1), dtype=float)
        self.P = np.eye(self.n, dtype=float)
        self.Q = np.eye(self.n) * config.process_var
        self.H = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], dtype=float)
        self.R = np.eye(2) * config.meas_var_pos
        self._lambda = config.alpha**2 * (self.n + config.kappa) - self.n
        self._wm, self._wc = self._weights()

    def _weights(self):
        lam = self._lambda
        n = self.n
        wm = np.full(2 * n + 1, 0.5 / (n + lam))
        wc = np.full(2 * n + 1, 0.5 / (n + lam))
        wm[0] = lam / (n + lam)
        wc[0] = lam / (n + lam) + (1 - self.cfg.alpha**2 + self.cfg.beta)
        return wm, wc

    def _sigma_points(self, x, P):
        n = self.n
        lam = self._lambda
        S = np.linalg.cholesky((n + lam) * P)
        points = [x]
        for i in range(n):
            col = S[:, i : i + 1]
            points.append(x + col)
            points.append(x - col)
        return np.hstack(points)

    def predict(self, dt: Optional[float] = None):
        dt = dt or self.cfg.dt
        Xsig = self._sigma_points(self.x, self.P)
        # Constant velocity model
        for i in range(Xsig.shape[1]):
            x, y, vx, vy = Xsig[:, i]
            Xsig[0, i] = x + vx * dt
            Xsig[1, i] = y + vy * dt
        x_pred = np.sum(self._wm * Xsig, axis=1, keepdims=True)
        P_pred = np.zeros((self.n, self.n))
        for i in range(Xsig.shape[1]):
            dx = Xsig[:, i : i + 1] - x_pred
            P_pred += self._wc[i] * (dx @ dx.T)
        P_pred += self.Q
        self.x, self.P = x_pred, P_pred

    def update(self, z: np.ndarray):
        # Measurement is [x, y]
        Xsig = self._sigma_points(self.x, self.P)
        Zsig = self.H @ Xsig
        z_pred = np.sum(self._wm * Zsig, axis=1, keepdims=True)
        S = np.zeros((2, 2))
        for i in range(Zsig.shape[1]):
            dz = Zsig[:, i : i + 1] - z_pred
            S += self._wc[i] * (dz @ dz.T)
        S += self.R
        # Cross covariance
        Pxz = np.zeros((self.n, 2))
        for i in range(Xsig.shape[1]):
            dx = Xsig[:, i : i + 1] - self.x
            dz = Zsig[:, i : i + 1] - z_pred
            Pxz += self._wc[i] * (dx @ dz.T)
        K = Pxz @ np.linalg.inv(S)
        innovation = z - z_pred
        self.x = self.x + K @ innovation
        self.P = self.P - K @ S @ K.T

    def mahalanobis(self, z: np.ndarray) -> float:
        Xsig = self._sigma_points(self.x, self.P)
        Zsig = self.H @ Xsig
        z_pred = np.sum(self._wm * Zsig, axis=1, keepdims=True)
        S = np.zeros((2, 2))
        for i in range(Zsig.shape[1]):
            dz = Zsig[:, i : i + 1] - z_pred
            S += self._wc[i] * (dz @ dz.T)
        S += self.R
        diff = z - z_pred
        return float(diff.T @ np.linalg.inv(S) @ diff)
