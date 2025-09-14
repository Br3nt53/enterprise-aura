import time
from contextlib import contextmanager

from aura_v2.observability.metrics import metrics


@contextmanager
def span(name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        dur = (time.perf_counter() - start) * 1000
        metrics.observe(f"span.{name}.ms", dur)
