from __future__ import annotations

from typing import Dict

import numpy as np

from .kbest_murty import MurtyKBest


def kbest_to_marginals(C: np.ndarray, k: int, beta: float = 1.0) -> Dict[str, np.ndarray]:
    """
    Convert top-k assignments into approximate association marginals.
    Cost matrix C: shape (M,N)
    Returns:
      P: (M,N) probabilities
      Z: partition function sum(exp(-beta * cost))
    Unselected rows/cols in an assignment are implicitly unmatched (only pairs present in solution).
    """
    solver = MurtyKBest(C)
    sols = solver.solve(k)
    if not sols:
        return {"P": np.zeros_like(C), "Z": 0.0, "solutions": []}

    weights = []
    for s in sols:
        w = np.exp(-beta * s.total_cost)
        weights.append(w)
    Z = np.sum(weights)

    P = np.zeros_like(C, dtype=float)
    for s, w in zip(sols, weights, strict=False):
        for r, c in s.assignment:
            P[r, c] += w

    if Z > 0:
        P /= Z

    return {"P": P, "Z": Z, "solutions": sols}
