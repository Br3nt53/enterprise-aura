from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np

from .hypothesis_enumerator import enumerate_hypotheses
from .likelihoods import compute_hypothesis_likelihood


def cluster_jpda(
    det_indices: List[int],
    trk_indices: List[int],
    lh_matrix: np.ndarray,  # (M,N) detection likelihoods (after gating, zeros where invalid)
    gating_mask: np.ndarray,  # (M,N) binary
    P_D: float,
    lambda_FA: float,
    max_hypotheses: int = 200,
) -> Dict[str, np.ndarray]:
    """
    Returns:
      P_assoc: (M,N) marginal association probabilities
      P_missed: (N,) probability of miss for each track
    """
    allowed = {d: [t for t in trk_indices if gating_mask[d, t]] for d in det_indices}
    hyps = enumerate_hypotheses(det_indices, trk_indices, allowed, max_hypotheses=max_hypotheses)

    track_lh_map = {}
    for d in det_indices:
        for t in trk_indices:
            if gating_mask[d, t]:
                track_lh_map[(d, t)] = lh_matrix[d, t]

    hyp_weights = []
    for h in hyps:
        w = compute_hypothesis_likelihood(
            h, track_lh_map, len(trk_indices), P_D, lambda_FA, len(det_indices)
        )
        hyp_weights.append(w)

    total = sum(hyp_weights) + 1e-15
    hyp_weights = [w / total for w in hyp_weights]

    M = lh_matrix.shape[0]
    N = lh_matrix.shape[1]
    P_assoc = np.zeros((M, N), dtype=np.float64)
    P_miss = np.zeros(N, dtype=np.float64)

    for h, w in zip(hyps, hyp_weights):
        for d, t in h["pairs"]:
            P_assoc[d, t] += w
        for t in h["unmatched_tracks"]:
            P_miss[t] += w

    # Ensure consistency: P_miss + Σ_d P_assoc[d,t] ≈ 1
    return {
        "P_assoc": P_assoc,
        "P_miss": P_miss,
        "num_hypotheses": len(hyps),
        "norm_check": np.max(np.abs(P_miss + P_assoc.sum(axis=0) - 1.0)),
    }
