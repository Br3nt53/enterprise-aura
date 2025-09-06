# aura_v2/infrastructure/monitoring/telemetry.py
from prometheus_client import Counter, Histogram, Gauge
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger import JaegerExporter
import structlog

class TelemetrySystem:
    """Complete observability for the tracking system"""
    
    def __init__(self, config: Dict[str, Any]):
        # Metrics
        self.tracks_created = Counter(
            'aura_tracks_created_total',
            'Total number of tracks created'
        )
        self.tracks_deleted = Counter(
            'aura_tracks_deleted_total',
            'Total number of tracks deleted'
        )
        self.active_tracks = Gauge(
            'aura_active_tracks',
            'Current number of active tracks'
        )
        self.pipeline_latency = Histogram(
            'aura_pipeline_latency_seconds',
            'Processing latency in seconds',
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
        )
        self.threat_detections = Counter(
            'aura_threat_detections_total',
            'Total threat detections by level',
            ['threat_level']
        )
        
        # Tracing
        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource.create({
                    "service.name": "aura-tracker"
                })
            )
        )
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(
                JaegerExporter(
                    agent_host_name=config['jaeger_host'],
                    agent_port=config['jaeger_port']
                )
            )
        )
        self.tracer = trace.get_tracer(__name__)
        
        # Structured Logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        self.logger = structlog.get_logger()