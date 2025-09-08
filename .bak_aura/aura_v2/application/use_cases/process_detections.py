# Next step: Replace placeholder with real implementation
# aura_v2/application/use_cases/process_detections.py

from datetime import datetime
from typing import List
from dataclasses import dataclass

from ...domain.entities import Detection, Track
from ...infrastructure.tracking.modern_tracker import ModernTracker, TrackingResult


@dataclass
class ProcessDetectionsResult:
    tracks: List[Track]
    processing_time_ms: float


class ProcessDetectionsUseCase:
    """Core use case for processing detections into tracks"""

    def __init__(self, tracker: ModernTracker):
        self.tracker = tracker

    async def execute(
        self, detections: List[Detection], timestamp: datetime
    ) -> ProcessDetectionsResult:
        """Process detections and return tracking result"""
        result: TrackingResult = await self.tracker.update(detections, timestamp)

        return ProcessDetectionsResult(
            tracks=result.active_tracks, processing_time_ms=result.processing_time_ms
        )


# This gives you proper layering: API -> Pipeline -> Use Case -> Domain
