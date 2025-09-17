from __future__ import annotations

from typing import Any, Callable

import numpy as np


class SRUKFConfig:
    def __init__(self, **kw: Any) -> None:
        self.__dict__.update(kw)


class SquareRootUKF:
    """Tiny shim API used by tests."""

    def __init__(self, *args: Any, **kw: Any) -> None:
        fx: Callable[[np.ndarray, float], np.ndarray] | None = None
        hx: Callable[[np.ndarray], np.ndarray] | None = None
        dim = int(kw.get("dim", 2))
        q = float(kw.get("process_var", kw.get("q", 1.0)))
        r = float(kw.get("meas_var", kw.get("r", 1.0)))
        dt = float(kw.get("dt", 1.0))

        # SRUKFConfig first positional
        if args and isinstance(args[0], SRUKFConfig):
            c = args[0].__dict__
            dim = int(c.get("dim", dim))
            q = float(c.get("process_var", c.get("q", q)))
            r = float(c.get("meas_var", c.get("r", r)))
            dt = float(c.get("dt", dt))
            args = args[1:]

        rest = list(args)
        if rest and callable(rest[0]):
            fx = rest.pop(0)
        if rest and callable(rest[0]):
            hx = rest.pop(0)
        if rest:
            try:
                dim = int(rest[0])
            except Exception:
                pass

        self.dt = dt
        self._fx = fx or (lambda x, d: x)
        self._hx = hx or (lambda x: x)
        self._q = q
        self._r = r
        self._init_mats(dim)
        self.set_state(np.zeros((dim, 1)))

    def _init_mats(self, dim: int) -> None:
        self.dim = dim
        self.x = np.zeros((dim, 1))
        self.P = np.eye(dim)
        self.Q = np.eye(dim) * self._q

    def set_state(self, x: np.ndarray, P: np.ndarray | None = None) -> None:
        x = np.asarray(x, float).reshape(-1, 1)
        if x.shape[0] != self.dim:
            self._init_mats(x.shape[0])
        self.x = x
        if P is not None:
            self.P = np.asarray(P, float).reshape(self.dim, self.dim)

    def predict(self, dt: float | None = None) -> None:
        if dt is not None:
            self.dt = float(dt)
        self.x = self._fx(self.x, self.dt)
        self.P = self.P + self.Q

    def update(self, z: np.ndarray) -> None:
        z = np.asarray(z, float).reshape(-1, 1)
        m = z.shape[0]
        H = np.zeros((m, self.dim))
        H[np.arange(m), np.arange(m)] = 1.0
        Rm = np.eye(m) * self._r
        y = z - (H @ self.x)
        S = H @ self.P @ H.T + Rm
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(self.dim) - K @ H) @ self.P
