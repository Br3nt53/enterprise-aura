"""Telemetry client for capturing and exporting traces and metrics."""

from contextlib import contextmanager
from typing import Any, Dict
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import get_tracer, set_tracer_provider


class TelemetryClient:
    def __init__(self, config: Dict[str, Any]):
        service_name = config.get("service_name", "aura-v2")
        self.tracer_provider = TracerProvider(
            resource=Resource.create({"service.name": service_name})
        )
        set_tracer_provider(self.tracer_provider)
        self.tracer = get_tracer(__name__)

    @contextmanager
    def start_span(self, name: str, attributes: Dict[str, Any] = None):
        with self.tracer.start_as_current_span(name, attributes=attributes) as span:
            yield span

    def shutdown(self):
        self.tracer_provider.shutdown()
