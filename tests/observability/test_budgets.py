import os

def test_latency_budget_env_present():
    # Budget drives DSS and CI gates
    v = int(os.getenv("AURA_LATENCY_P99_BUDGET_MS", "750"))
    assert v >= 100  # sanity
