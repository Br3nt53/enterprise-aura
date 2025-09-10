import os
import time
import random
import psutil

import pytest

from aura_v2.observability.metrics_validator import (
    validate_latency_ms,
    validate_id_switch_rate,
    validate_memory_mb,
)

STRICT = os.getenv("AURA_METRICS_STRICT", "0") == "1"

@pytest.mark.skipif(not STRICT, reason="strict metrics disabled")
def test_latency_budget_p99_under_budget():
    # Simulate 500 frames with ~5ms processing, with a few spikes
    lat = [5.0 + random.random() for _ in range(495)] + [12.0, 15.0, 20.0, 9.0, 8.0]
    p99, avg = validate_latency_ms(list(lat))
    assert p99 <= float(os.getenv("AURA_P99_LATENCY_MS_BUDGET", "750"))

@pytest.mark.skipif(not STRICT, reason="strict metrics disabled")
def test_id_switch_rate_under_cap():
    # Example: 3 switches across 500 associations = 0.006
    rate = validate_id_switch_rate(3, 500)
    assert rate <= float(os.getenv("AURA_MAX_ID_SWITCH_RATE", "0.02"))

@pytest.mark.skipif(not STRICT, reason="strict metrics disabled")
def test_memory_under_cap():
    proc = psutil.Process()
    rss_mb = proc.memory_info().rss / (1024 * 1024)
    validate_memory_mb(rss_mb)  # cap defaults to 1024MB
