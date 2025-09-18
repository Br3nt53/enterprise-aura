from __future__ import annotations

import os
from typing import Iterable, Tuple


def p99(values: Iterable[float]) -> float:
    data = sorted(values)
    if not data:
        return 0.0
    k = int(round(0.99 * (len(data) - 1)))
    return data[k]


def validate_latency_ms(latencies_ms: Iterable[float]) -> Tuple[float, float]:
    budget = float(os.getenv("AURA_P99_LATENCY_MS_BUDGET", "750"))
    p99v = p99(latencies_ms)
    avg = sum(latencies_ms) / max(
        1, len(list(latencies_ms))
    )  # list consumed above; pass generator lists in
    if p99v > budget:
        raise AssertionError(f"P99 latency {p99v:.1f}ms exceeds budget {budget:.1f}ms")
    return p99v, avg


def validate_id_switch_rate(switches: int, total_associations: int) -> float:
    if total_associations <= 0:
        return 0.0
    rate = switches / float(total_associations)
    cap = float(os.getenv("AURA_MAX_ID_SWITCH_RATE", "0.02"))
    if rate > cap:
        raise AssertionError(f"ID-switch rate {rate:.4f} exceeds cap {cap:.4f}")
    return rate


def validate_memory_mb(current_mb: float, cap_mb: float | None = None) -> float:
    cap = cap_mb if cap_mb is not None else float(os.getenv("AURA_MAX_MEMORY_MB", "1024"))
    if current_mb > cap:
        raise AssertionError(f"Memory {current_mb:.1f}MB exceeds cap {cap:.1f}MB")
    return current_mb
