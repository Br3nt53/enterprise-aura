from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import numpy as np


@dataclass
class SRUKFConfig:
    n: int  # State dimension
    m: int  # Measurement dimension
    alpha: float = 1e-3
    beta: float = 2.0
    kappa: float = 0.0
    process_noise: float = 1.0
    meas_noise: float = 0.5
    adaptive: bool = False


class SquareRootUKF:
    """
    Square-root Unscented Kalman Filter for a generic state with
    user-supplied transition f(x, dt) and measurement h(x).
    """

    def __init__(
        self,
        cfg: SRUKFConfig,
        f: Callable[[np.ndarray, float], np.ndarray],
        h: Callable[[np.ndarray], np.ndarray],
    ):
        self.cfg = cfg
        self.f = f
        self.h = h
        self.n = cfg.n
        self.m = cfg.m
        self.x = np.zeros((self.n, 1), dtype=float)
        self.S = np.eye(self.n)  # Cholesky factor of state covariance
        self.R_sqrt = np.eye(self.m) * np.sqrt(cfg.meas_noise)
        self.Q_sqrt = np.eye(self.n) * np.sqrt(cfg.process_noise)
        self._lambda = cfg.alpha**2 * (self.n + cfg.kappa) - self.n
        self.gamma = np.sqrt(self.n + self._lambda)
        self.wm, self.wc = self._weights()
        # Innovation buffer for adaptive noise
        self._innov_hist: list[np.ndarray] = []

    def _weights(self):
        lam = self._lambda
        n = self.n
        wm = np.full(2 * n + 1, 0.5 / (n + lam))
        wc = np.full(2 * n + 1, 0.5 / (n + lam))
        wm[0] = lam / (n + lam)
        wc[0] = lam / (n + lam) + (1 - self.cfg.alpha**2 + self.cfg.beta)
        return wm, wc

    def set_state(self, mean: np.ndarray, S: np.ndarray):
        assert mean.shape == (self.n, 1)
        assert S.shape == (self.n, self.n)
        self.x = mean.copy()
        self.S = S.copy()

    def sigma_points(self) -> np.ndarray:
        # S is lower or upper (we treat generically)
        if not np.allclose(self.S, np.tril(self.S)):
            # Ensure S is lower-triangular
            self.S = np.linalg.cholesky(self.S @ self.S.T)
        points = [self.x]
        for i in range(self.n):
            col = self.S[:, i : i + 1] * self.gamma
            points.append(self.x + col)
            points.append(self.x - col)
        return np.hstack(points)  # (n, 2n+1)

    def predict(self, dt: float):
        X = self.sigma_points()
        X_pred = np.zeros_like(X)
        for i in range(X.shape[1]):
            X_pred[:, i : i + 1] = self.f(X[:, i : i + 1], dt)
        x_mean = (X_pred * self.wm).sum(axis=1, keepdims=True)

        # Form matrix for QR: sqrt-weighted deviations + process noise sqrt
        devs = X_pred - x_mean
        W = np.sqrt(self.wc)[None, :]
        A = np.hstack([devs * W, self.Q_sqrt])
        # QR decomposition of Aᵀ
        _, R = np.linalg.qr(A.T, mode="reduced")
        S_new = R.T
        # Force lower-triangular if needed
        self.x = x_mean
        # Enforce symmetry via re-Cholesky:
        P_approx = S_new @ S_new.T
        self.S = np.linalg.cholesky(0.5 * (P_approx + P_approx.T))

    def update(self, z: np.ndarray):
        assert z.shape == (self.m, 1)
        X = self.sigma_points()
        Z = np.zeros((self.m, X.shape[1]))
        for i in range(X.shape[1]):
            Z[:, i : i + 1] = self.h(X[:, i : i + 1])

        z_mean = (Z * self.wm).sum(axis=1, keepdims=True)
        Z_devs = Z - z_mean
        X_devs = X - self.x

        # Measurement covariance sqrt via QR
        Wc = np.sqrt(self.wc)[None, :]
        B = np.hstack([Z_devs * Wc, self.R_sqrt])
        _, Rz = np.linalg.qr(B.T, mode="reduced")
        Sz = Rz.T
        P_xz = (X_devs * self.wc) @ Z_devs.T  # (n x m)

        # Solve for K using triangular solves:
        # Sz is sqrt of S_z S_zᵀ
        # First solve Szᵀ u = P_xzᵀ  => u = (Szᵀ)⁻¹ P_xzᵀ
        # Then K = uᵀ Sz⁻¹
        u = np.linalg.solve(Sz.T, P_xz.T)
        K = u.T @ np.linalg.inv(Sz)

        innovation = z - z_mean
        self._innov_hist.append(innovation.copy())

        self.x = self.x + K @ innovation

        # Update covariance sqrt:
        # Joseph-like stable update using concatenated matrix
        U = K @ Sz
        # Build composite deviations for QR
        # Combine state deviations minus projected part and process noise sqrt
        C = np.hstack([(X_devs - (K @ Z_devs)) * np.sqrt(self.wc)[None, :], self.Q_sqrt, -U])
        _, Rs = np.linalg.qr(C.T, mode="reduced")
        S_new = Rs.T
        P_approx = S_new @ S_new.T
        self.S = np.linalg.cholesky(0.5 * (P_approx + P_approx.T))

        # Adaptive measurement noise (optional)
        if self.cfg.adaptive and len(self._innov_hist) >= 5:
            self._adapt_measurement_noise()

    def _adapt_measurement_noise(self):
        # Simple exponential moving average of innovation covariance
        hist = np.hstack(self._innov_hist[-20:])
        mean = hist.mean(axis=1, keepdims=True)
        diffs = hist - mean
        cov = (diffs @ diffs.T) / hist.shape[1]
        # Blend
        blend = 0.95 * (self.R_sqrt @ self.R_sqrt.T) + 0.05 * cov
        # Re-factor
        self.R_sqrt = np.linalg.cholesky(0.5 * (blend + blend.T))

    def mahalanobis(self, z: np.ndarray) -> float:
        # Innovation based gating reference
        X = self.sigma_points()
        Z = np.zeros((self.m, X.shape[1]))
        for i in range(X.shape[1]):
            Z[:, i : i + 1] = self.h(X[:, i : i + 1])
        z_mean = (Z * self.wm).sum(axis=1, keepdims=True)
        innovation = z - z_mean
        # Compute measurement covariance via Z devs + R
        Z_devs = Z - z_mean
        Wc = self.wc
        Sz = self.R_sqrt.copy()
        # (Optional more exact: recompute as in update)
        # Triangular solve for Mahalanobis
        v = np.linalg.solve(Sz, innovation)
        return float(v.T @ v)
