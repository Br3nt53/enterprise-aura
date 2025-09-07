# aura_v2/application/pipelines/tracking_pipeline.py
from typing import AsyncIterator
import asyncio
from dataclasses import dataclass
from datetime import datetime
from ...application.use_cases.process_detections import ProcessDetectionsUseCase, ProcessDetectionsCommand

@dataclass
class PipelineContext:
    """Context passed through pipeline stages"""
    config: 'Config'
    telemetry: 'TelemetryClient'
    cancellation_token: asyncio.Event

class TrackingPipeline:
    """Main tracking pipeline orchestrator"""
    
    def __init__(
        self,
        detection_source: 'DetectionSource',
        process_detections_use_case: ProcessDetectionsUseCase,
        evaluation_use_case: 'EvaluationUseCase',
        output_sink: 'OutputSink'
    ):
        self.detection_source = detection_source
        self.process_detections = process_detections_use_case
        self.evaluation = evaluation_use_case
        self.output_sink = output_sink
    
    async def run(self, context: PipelineContext) -> None:
        """Run the tracking pipeline"""
        try:
            async for detections_batch in self.detection_source.stream():
                # Check for cancellation
                if context.cancellation_token.is_set():
                    break
                
                # Process detections
                result = await self.process_detections.execute(
                    ProcessDetectionsCommand(
                        detections=detections_batch,
                        timestamp=datetime.now()
                    )
                )
                
                # Evaluate if needed
                if context.config.enable_evaluation:
                    metrics = await self.evaluation.execute(result.active_tracks)
                    await self.output_sink.write_metrics(metrics)
                
                # Output tracks
                await self.output_sink.write_tracks(result.active_tracks)
                
        except Exception as e:
            context.telemetry.record_error(e)
            raise