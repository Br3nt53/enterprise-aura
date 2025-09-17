from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np
from scipy.optimize import linear_sum_assignment


def _sanitize_cost(C):
    C = np.asarray(C, float)
    finite = C[np.isfinite(C)]
    fill = (finite.max() if finite.size else 1.0) * 1e6
    return np.where(np.isfinite(C), C, fill)


@dataclass(order=True)
class _MurtyNode:
    total_cost: float
    # Not part of ordering:
    fixed_pairs: List[Tuple[int, int]] = field(compare=False, default_factory=list)
    forbidden_pairs: List[Tuple[int, int]] = field(compare=False, default_factory=list)
    assignment: List[Tuple[int, int]] = field(compare=False, default_factory=list)


class MurtyKBest:
    """
    Murty's algorithm for k-best assignment problems.
    Assumes rectangular cost matrix C (shape M x N); if M != N,
    we allow dummy rows/cols by padding to square (or treat as rectangular with Hungarian).
    Costs should represent additive objective (lower is better).
    Forbidden pairs are implemented by setting cost to +inf temporarily.
    """

    def __init__(self, C: np.ndarray):
        if C.ndim != 2:
            raise ValueError("Cost matrix must be 2D")
        self.original = C
        self.M, self.N = C.shape

    def _apply_constraints(
        self, fixed: List[Tuple[int, int]], forbid: List[Tuple[int, int]]
    ) -> np.ndarray:
        C = self.original.copy()
        big = np.inf

        # Enforce fixed pairs by:
        #  - For a fixed (i,j), set row i to inf except column j
        #  - For column j, set all other rows to inf
        # This forces Hungarian to pick (i,j)
        for i, j in fixed:
            for col in range(self.N):
                if col != j:
                    C[i, col] = big
            for row in range(self.M):
                if row != i:
                    C[row, j] = big

        for i, j in forbid:
            C[i, j] = big
        return C

    def _solve(
        self, fixed: List[Tuple[int, int]], forbid: List[Tuple[int, int]]
    ) -> Optional[_MurtyNode]:
        C = self._apply_constraints(fixed, forbid)
        if np.isinf(C).all():
            return None

        row_ind, col_ind = linear_sum_assignment(_sanitize_cost(C))
        # Validate feasibility: any chosen inf => infeasible
        pairs = []
        total_cost = 0.0
        for r, c in zip(row_ind, col_ind, strict=False):
            cost = C[r, c]
            if math.isinf(cost):
                return None
            pairs.append((r, c))
            total_cost += float(cost)
        return _MurtyNode(
            total_cost=total_cost,
            fixed_pairs=fixed.copy(),
            forbidden_pairs=forbid.copy(),
            assignment=pairs,
        )

    def solve(self, k: int) -> List[_MurtyNode]:
        solutions: List[_MurtyNode] = []

        root = self._solve([], [])
        if root is None:
            return sorted(solutions, key=lambda n: float(n.total_cost))
        heap: List[_MurtyNode] = []
        heapq.heappush(heap, root)

        while heap and len(solutions) < k:
            best = heapq.heappop(heap)
            solutions.append(best)

            # Branch: for each position in assignment create a subproblem
            # Partition:
            #   For current best assignment a0,a1,...,an-1
            #   For branch at index b:
            #     fixed = assignment[:b]
            #     forbid = assignment[b]
            for idx, (ri, ci) in enumerate(best.assignment):
                fixed_prefix = best.assignment[:idx]
                forbid_pair = (ri, ci)
                node = self._solve(fixed=fixed_prefix, forbid=best.forbidden_pairs + [forbid_pair])
                if node:
                    heapq.heappush(heap, node)

        return sorted(solutions, key=lambda n: float(n.total_cost))
