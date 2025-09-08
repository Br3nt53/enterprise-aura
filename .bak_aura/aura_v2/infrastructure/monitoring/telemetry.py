# aura_v2/infrastructure/monitoring/telemetry.py
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict
import time


class TelemetrySystem:
    """Complete observability for the tracking system"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = getLogger(__name__)
        self.metrics = {}

    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric value"""
        self.metrics[name] = {
            "value": value,
            "timestamp": time.time(),
            "tags": tags or {},
        }

    @contextmanager
    def track_operation(self, name: str):
        """Context manager to track operation timing"""
        start_time = time.time()
        try:
            yield
            duration = time.time() - start_time
            self.record_metric(f"{name}.duration", duration)
            self.record_metric(f"{name}.success", 1)
        except Exception as e:
            duration = time.time() - start_time
            self.record_metric(f"{name}.duration", duration)
            self.record_metric(f"{name}.failure", 1)
            self.logger.error(f"Operation {name} failed: {e}")
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """Get all recorded metrics"""
        return self.metrics.copy()
