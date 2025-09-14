from __future__ import annotations

from typing import Protocol, Sequence

import numpy as np

from .iou import aabb_iou_matrix


class TrackStateProvider(Protocol):
    id: str

    def position(self) -> tuple[float, float]: ...
    def covariance(self) -> np.ndarray: ...
    def bbox(self) -> list[float] | tuple[float, float, float, float]: ...


class DetectionProvider(Protocol):
    id: str
    position: tuple[float, float]
    bbox: list[float]
    score: float


def mahalanobis_matrix(
    detections: Sequence[DetectionProvider], tracks: Sequence[TrackStateProvider]
) -> np.ndarray:
    M, N = len(detections), len(tracks)
    out = np.zeros((M, N), dtype=np.float32)
    for j, t in enumerate(tracks):
        cov = t.covariance()
        if cov.shape != (2, 2):
            raise ValueError("Covariance must be 2x2 for gating here.")
        cov_inv = np.linalg.inv(cov + 1e-6 * np.eye(2))
        tx, ty = t.position()
        for i, d in enumerate(detections):
            dx, dy = d.position
            diff = np.array([[dx - tx], [dy - ty]], dtype=np.float32)
            out[i, j] = float(diff.T @ cov_inv @ diff)
    return out


def build_hybrid_cost(
    detections: Sequence[DetectionProvider],
    tracks: Sequence[TrackStateProvider],
    weights: dict[str, float],
    chi_sq_gate: float,
    max_cost: float,
) -> np.ndarray:
    if not detections or not tracks:
        return np.zeros((len(detections), len(tracks)), dtype=np.float32)

    det_b = np.array([d.bbox for d in detections], dtype=np.float32)
    trk_b = np.array([t.bbox() for t in tracks], dtype=np.float32)

    iou = aabb_iou_matrix(det_b, trk_b)  # (M,N)
    iou_cost = 1.0 - iou

    maha = mahalanobis_matrix(detections, tracks)
    # Gate: if maha > chi_sq_gate => set to large cost
    gated = np.where(maha > chi_sq_gate, np.inf, maha)
    # Normalize finite mahal distances
    finite = gated[np.isfinite(gated)]
    if finite.size:
        maha_norm = gated / (finite.max() + 1e-6)
    else:
        maha_norm = gated

    conf = np.array([d.score for d in detections], dtype=np.float32)
    conf_cost = (1.0 / np.clip(conf, 1e-3, 1.0))[:, None]
    conf_cost /= conf_cost.max() + 1e-6

    total = (
        weights["iou"] * iou_cost
        + weights["motion"] * maha_norm
        + weights.get("confidence", 0.0) * conf_cost
    )

    return np.where(total > max_cost, np.inf, total)
