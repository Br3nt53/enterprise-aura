# aura_v2/application/pipelines/tracking_pipeline.py
from typing import List
import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone  # Import timezone
from ..use_cases.process_detections import ProcessDetectionsUseCase, ProcessDetectionsCommand
from ...domain.entities import Detection, Track


@dataclass
class PipelineContext:
    config: 'Config'
    telemetry: 'TelemetryClient'
    cancellation_token: asyncio.Event

class TrackingPipeline:
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
        # ... implementation ...
    
    async def process(self, detections: List[dict]) -> List[Track]:
        """ Processes a single batch of detections for testing purposes. """
        detection_objects = [
            Detection.from_dict(d) for d in detections
        ]

        result = await self.process_detections.execute(
            ProcessDetectionsCommand(
                detections=detection_objects,
                timestamp=datetime.now(timezone.utc)  # CRITICAL FIX: Use timezone-aware datetime
            )
        )
        return result.active_tracks