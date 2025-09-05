# domain/pipeline/models.py
@dataclass
class PipelineStage:
    name: str
    retry_policy: RetryPolicy
    timeout: timedelta
    
class Pipeline:
    def __init__(self, stages: List[PipelineStage]):
        self.stages = stages
    
    async def execute(self, context: PipelineContext) -> PipelineResult:
        for stage in self.stages:
            context = await self._execute_stage(stage, context)
        return PipelineResult(context)

# application/pipelines/evaluation_pipeline.py
class EvaluationPipelineBuilder:
    def build(self, config: PipelineConfig) -> Pipeline:
        return Pipeline([
            DataIngestionStage(
                sources=config.data_sources,
                validators=[JSONLValidator(), SchemaValidator()]
            ),
            PreprocessingStage(
                filters=[TimeRangeFilter(), ConfidenceFilter()],
                transformers=[CoordinateNormalizer()]
            ),
            TrackingStage(
                tracker=self.tracker_factory.create(config.tracker_type),
                association_strategy=HungarianAssociation()
            ),
            EvaluationStage(
                metrics=[MOTAMetric(), HOTAMetric(), IDFMetric()],
                aggregators=[MeanAggregator(), PercentileAggregator()]
            ),
            ReportingStage(
                generators=[JSONReport(), HTMLReport(), TensorBoardReport()],
                publishers=[FilePublisher(), S3Publisher(), SlackPublisher()]
            )
        ])

# infrastructure/orchestration/pipeline_executor.py
class AsyncPipelineExecutor:
    def __init__(self, 
                 circuit_breaker: CircuitBreaker,
                 telemetry: TelemetryClient):
        self.circuit_breaker = circuit_breaker
        self.telemetry = telemetry
    
    async def execute(self, pipeline: Pipeline, context: Context) -> Result:
        span = self.telemetry.start_span("pipeline_execution")
        try:
            async with self.circuit_breaker:
                result = await pipeline.execute(context)
                self.telemetry.record_success(span)
                return result
        except Exception as e:
            self.telemetry.record_failure(span, e)
            raise