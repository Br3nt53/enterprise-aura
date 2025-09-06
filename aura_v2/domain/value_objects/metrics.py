from __future__ import annotations
from typing import Annotated, cast
import numpy as np

# Simple alias for covariance matrices; keep numpy dependency minimal
Covariance = np.ndarray  # shape validation can be done at use-sites

def make_covariance(diag: list[float] | tuple[float, ...]) -> Covariance:
    d = np.asarray(diag, dtype=float)
    return np.diag(d)

def is_symmetric_positive_semidefinite(m: np.ndarray, atol: float = 1e-8) -> bool:
    if m.ndim != 2 or m.shape[0] != m.shape[1]:
        return False
    if not np.allclose(m, m.T, atol=atol):
        return False
    eigvals = np.linalg.eigvalsh(m)
    return np.all(eigvals >= -atol)
