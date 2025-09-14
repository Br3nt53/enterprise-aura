from __future__ import annotations
from typing import List, Tuple, Dict
import numpy as np
from scipy.optimize import linear_sum_assignment
from .hungarian_costs import combined_cost


def build_cost_matrix(
    detections: List[Dict],
    tracks: List[Dict],
    weights: Dict[str, float],
    max_cost: float,
) -> np.ndarray:
    M, N = len(detections), len(tracks)
    C = np.full((M, N), fill_value=max_cost, dtype=float)
    for i, d in enumerate(detections):
        for j, t in enumerate(tracks):
            cost = combined_cost(d["bbox"], t["bbox"], d.get("score", 1.0), weights)
            C[i, j] = min(cost, max_cost)
    return C


def solve_assignment(
    C: np.ndarray, max_cost: float
) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    row_ind, col_ind = linear_sum_assignment(C)
    matches, unm_det, unm_trk = [], [], []
    assigned_trk = set()
    for r, c in zip(row_ind, col_ind):
        if C[r, c] < max_cost:
            matches.append((r, c))
            assigned_trk.add(c)
        else:
            unm_det.append(r)
    for r in range(C.shape[0]):
        if r not in [m[0] for m in matches]:
            unm_det.append(r)
    for c in range(C.shape[1]):
        if c not in assigned_trk:
            unm_trk.append(c)
    return matches, sorted(set(unm_det)), sorted(set(unm_trk))
