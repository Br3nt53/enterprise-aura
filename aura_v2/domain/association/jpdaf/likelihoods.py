from __future__ import annotations

import math
from typing import Dict, List, Tuple

import numpy as np


def gaussian_likelihood(residual: np.ndarray, S_inv: np.ndarray, log_det_S: float) -> float:
    # residual: (m,1)
    # p(z|track) = (2π)^{-m/2} |S|^{-1/2} exp(-0.5 * r^T S^{-1} r)
    m = residual.shape[0]
    quad = float(residual.T @ S_inv @ residual)
    log_norm = -0.5 * (m * math.log(2 * math.pi) + log_det_S + quad)
    return math.exp(log_norm)


def compute_hypothesis_likelihood(
    hypothesis: Dict,
    track_lh_map: Dict[Tuple[int, int], float],
    n_tracks: int,
    P_D: float,
    lambda_FA: float,
    n_detections: int,
) -> float:
    """
    track_lh_map: (d,t) -> p(z_d | t)
    λ_FA: expected false alarms per frame (simplified)
    """
    pairs = hypothesis["pairs"]
    unmatched_tracks = hypothesis["unmatched_tracks"]
    unmatched_dets = hypothesis["unmatched_detections"]

    if not pairs and not unmatched_dets and not unmatched_tracks:
        return 1e-12

    # Product of matched detection likelihoods
    prod_lh = 1.0
    for d, t in pairs:
        prod_lh *= track_lh_map[(d, t)]

    # Missed detection factor
    miss_factor = (1 - P_D) ** len(unmatched_tracks)

    # False alarm factor (Poisson) approximate
    fa_factor = (lambda_FA ** len(unmatched_dets)) * math.exp(-lambda_FA)

    return prod_lh * miss_factor * fa_factor
