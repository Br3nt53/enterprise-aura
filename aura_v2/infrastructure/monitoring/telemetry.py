from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

# aura_v2/infrastructure/monitoring/telemetry.py
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

from prometheus_client import Counter, Histogram, Gauge
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

from opentelemetry import trace, metrics
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

from opentelemetry.exporter.jaeger import JaegerExporter
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

import structlog
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider


from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

class TelemetrySystem:
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

    """Complete observability for the tracking system"""
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

    
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

    def __init__(self, config: Dict[str, Any]):
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        # Metrics
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        self.tracks_created = Counter(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            'aura_tracks_created_total',
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            'Total number of tracks created'
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        self.tracks_deleted = Counter(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            'aura_tracks_deleted_total',
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            'Total number of tracks deleted'
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        self.active_tracks = Gauge(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            'aura_active_tracks',
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            'Current number of active tracks'
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        self.pipeline_latency = Histogram(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            'aura_pipeline_latency_seconds',
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            'Processing latency in seconds',
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        self.threat_detections = Counter(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            'aura_threat_detections_total',
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            'Total threat detections by level',
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            ['threat_level']
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        # Tracing
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        trace.set_tracer_provider(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            TracerProvider(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                resource=Resource.create({
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                    "service.name": "aura-tracker"
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                })
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        trace.get_tracer_provider().add_span_processor(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            BatchSpanProcessor(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                JaegerExporter(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                    agent_host_name=config['jaeger_host'],
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                    agent_port=config['jaeger_port']
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        self.tracer = trace.get_tracer(__name__)
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        # Structured Logging
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        structlog.configure(
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            processors=[
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                structlog.stdlib.filter_by_level,
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                structlog.stdlib.add_logger_name,
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                structlog.stdlib.add_log_level,
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                structlog.stdlib.PositionalArgumentsFormatter(),
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                structlog.processors.TimeStamper(fmt="iso"),
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                structlog.processors.StackInfoRenderer(),
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                structlog.processors.format_exc_info,
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                structlog.processors.UnicodeDecoder(),
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

                structlog.processors.JSONRenderer()
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            ],
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            context_class=dict,
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            logger_factory=structlog.stdlib.LoggerFactory(),
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

            cache_logger_on_first_use=True,
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        )
from contextlib import contextmanager
from logging import getLogger
from typing import Any, Dict

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Span, get_tracer, set_tracer_provider

        self.logger = structlog.get_logger()
