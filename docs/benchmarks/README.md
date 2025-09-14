# Association Benchmark Harness

Usage:
```bash
python scripts/benchmarks/association_benchmark.py --sizes 20x20,40x40,80x80 --k 15 --structure clustered --repeats 3
```

Metrics:
- Hungarian: Baseline single best assignment runtime
- Murty k-best: Top-K enumeration
- k-best JPDA: Marginal approximation from K solutions

Interpretation:
- If Murty runtime grows superlinearly with K or dimension, consider tighter gating or cluster decomposition.
- Compare k-best marginals vs brute JPDA (for small matrices) to evaluate approximation error.
