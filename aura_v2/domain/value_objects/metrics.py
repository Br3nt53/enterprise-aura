# aura_v2/domain/value_objects/metrics.py

import numpy as np
from scipy.spatial.distance import mahalanobis

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
    return bool(np.all(eigvals >= -atol))


class MahalanobisDistance:
    """Utility for computing Mahalanobis distance between points."""

    def __init__(self, covariance_matrix: np.ndarray):
        self.cov_matrix = covariance_matrix
        self.inv_cov_matrix = np.linalg.pinv(covariance_matrix)

    def distance(self, point1: np.ndarray, point2: np.ndarray) -> float:
        """Compute Mahalanobis distance between two points."""
        try:
            return float(mahalanobis(point1, point2, self.inv_cov_matrix))
        except Exception:
            # Fallback to Euclidean distance if covariance is singular
            return float(np.linalg.norm(point1 - point2))  # type: ignore

    def distance_to_mean(self, point: np.ndarray, mean: np.ndarray) -> float:
        """Compute Mahalanobis distance from point to mean."""
        return self.distance(point, mean)  # type: ignore
