from __future__ import annotations

from collections import defaultdict
from typing import Dict


class Metrics:
    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, list[float]] = defaultdict(list)

    def increment(self, name: str, value: int = 1):
        self.counters[name] += value

    def observe(self, name: str, value: float):
        self.histograms[name].append(value)

    def set_gauge(self, name: str, value: float):
        self.gauges[name] = value


metrics = Metrics()
