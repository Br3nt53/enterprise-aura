from __future__ import annotations

import random
import time
from statistics import quantiles

from aura_v2.application.pipeline.fusion_pipeline_factory import build_default_pipeline


class SensorReading:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


def main():
    pipeline = build_default_pipeline()
    tracks = []
    timings = []
    for _ in range(200):
        batch = [SensorReading(random.random() * 100, random.random() * 100) for _ in range(25)]
        start = time.perf_counter()
        tracks = pipeline.process_batch(batch, tracks)
        timings.append((time.perf_counter() - start) * 1000)
    p99 = quantiles(timings, n=100)[-1]
    print(f"P99(ms)={p99:.2f}")
    if p99 > 750:
        raise SystemExit("Latency budget exceeded")


if __name__ == "__main__":
    main()
