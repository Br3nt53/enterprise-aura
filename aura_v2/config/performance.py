import os

P99_LATENCY_BUDGET_MS = int(os.getenv("AURA_P99_LATENCY_MS_BUDGET", "750"))
