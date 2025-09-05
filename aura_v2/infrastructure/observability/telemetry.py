# infrastructure/observability/telemetry.py
class TelemetrySystem:
    def __init__(self, config: TelemetryConfig):
        self.metrics = PrometheusMetrics(config.metrics_port)
        self.tracing = JaegerTracing(config.jaeger_endpoint)
        self.logging = StructuredLogging(config.log_level)
    
    @contextmanager
    def track_operation(self, name: str):
        with self.tracing.span(name) as span:
            start = time.time()
            try:
                yield span
                self.metrics.increment(f"{name}.success")
            except Exception as e:
                self.metrics.increment(f"{name}.failure")
                span.set_error(e)
                raise
            finally:
                duration = time.time() - start
                self.metrics.histogram(f"{name}.duration", duration)