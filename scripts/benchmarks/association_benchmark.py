from __future__ import annotations

import argparse
import random
import time

import numpy as np
from scipy.optimize import linear_sum_assignment

try:
    from aura_v2.domain.association.jpdaf.kbest_jpda_solver import kbest_to_marginals
    from aura_v2.domain.association.jpdaf.kbest_murty import MurtyKBest
except ImportError:
    raise SystemExit("Ensure PYTHONPATH includes project root")


def random_cost_matrix(m: int, n: int, seed: int = 42, structure: str = "uniform"):
    rng = np.random.default_rng(seed)
    if structure == "uniform":
        return rng.random((m, n))
    if structure == "clustered":
        C = rng.random((m, n))
        # Introduce 3 low-cost corridors
        for _ in range(3):
            r = rng.integers(0, m)
            C[r, :] *= rng.uniform(0.05, 0.2)
        return C
    if structure == "diagonal_bias":
        C = rng.random((m, n))
        for i in range(min(m, n)):
            C[i, i] *= rng.uniform(0.01, 0.15)
        return C
    return rng.random((m, n))


def bench_hungarian(C: np.ndarray, repeats: int = 5):
    start = time.perf_counter()
    for _ in range(repeats):
        linear_sum_assignment(C)
    dur = (time.perf_counter() - start) * 1000 / repeats
    return dur


def bench_murty(C: np.ndarray, k: int, repeats: int = 3):
    start = time.perf_counter()
    for _ in range(repeats):
        solver = MurtyKBest(C)
        solver.solve(k)
    dur = (time.perf_counter() - start) * 1000 / repeats
    return dur


def bench_kbest_jpda(C: np.ndarray, k: int, repeats: int = 3):
    start = time.perf_counter()
    for _ in range(repeats):
        kbest_to_marginals(C, k=k)
    dur = (time.perf_counter() - start) * 1000 / repeats
    return dur


def summarize(m: int, n: int, k: int, structure: str):
    C = random_cost_matrix(m, n, seed=123, structure=structure)
    h_ms = bench_hungarian(C)
    k_ms = bench_murty(C, k)
    j_ms = bench_kbest_jpda(C, k)

    print(f"Matrix: {m}x{n}  structure={structure}")
    print(f"  Hungarian     : {h_ms:8.3f} ms")
    print(f"  Murty k={k}    : {k_ms:8.3f} ms")
    print(f"  k-best JPDA(k={k} approx): {j_ms:8.3f} ms")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=str, default="20x20,40x40,60x60")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument(
        "--structure",
        type=str,
        default="uniform",
        choices=["uniform", "clustered", "diagonal_bias"],
    )
    ap.add_argument("--repeats", type=int, default=1)
    args = ap.parse_args()

    for _ in range(args.repeats):
        for token in args.sizes.split(","):
            m, n = map(int, token.lower().split("x"))
            summarize(m, n, args.k, args.structure)


if __name__ == "__main__":
    main()
