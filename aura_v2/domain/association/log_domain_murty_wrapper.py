from __future__ import annotations

import numpy as np
from domain.association.jpdaf.kbest_murty import MurtyKBest


def log_domain_kbest_marginals(C: np.ndarray, k: int) -> np.ndarray:
    """
    Compute approximate marginals using log-domain stabilization:
      We treat C as cost (already -log likelihood or additive non-negative).
      P(d,t) ≈ Σ_{solutions containing (d,t)} exp(-cost_sol) / Z
    """
    solver = MurtyKBest(C)
    sols = solver.solve(k)
    if not sols:
        return np.zeros_like(C)
    costs = np.array([s.total_cost for s in sols])
    # log weights = -cost
    logw = -costs
    maxlog = np.max(logw)
    w = np.exp(logw - maxlog)
    Z = w.sum()
    P = np.zeros_like(C, dtype=float)
    for s, ws in zip(sols, w, strict=False):
        for r, c in s.assignment:
            P[r, c] += ws
    P /= Z + 1e-15
    return P
