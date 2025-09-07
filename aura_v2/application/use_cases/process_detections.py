from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from ...domain.entities import Detection, Track
from ...domain.events import DomainEvent
from ...infrastructure.tracking.modern_tracker import ModernTracker, TrackingResult


@dataclass
class ProcessDetectionsCommand:
    detections: List[Detection]
    timestamp: datetime


@dataclass
class ProcessDetectionsResult:
    active_tracks: List[Track]
    new_tracks: List[Track]
    deleted_tracks: List[Track]
    events: List[DomainEvent]


class ProcessDetectionsUseCase:
    def __init__(self, track_repository: "TrackRepository", track_manager: ModernTracker):
        self.track_repository = track_repository
        self.track_manager = track_manager

    async def execute(self, command: ProcessDetectionsCommand) -> ProcessDetectionsResult:
        """
        Orchestrates processing detections by loading state, calling the tracker, and saving results.
        """
        # 1) Load current state
        active_tracks = await self.track_repository.get_active_tracks()

        # 2) Synchronize tracker memory and ensure each loaded track has a KF
        self.track_manager.tracks = {t.id: t for t in active_tracks}
        for t in active_tracks:
            if t.id not in self.track_manager.kalman_filters:
                # Intentionally using the tracker's initializer
                self.track_manager._init_kf(t)  # noqa: SLF001

        # 3) Run tracker
        result: TrackingResult = await self.track_manager.update(
            command.detections,
            command.timestamp,
        )

        # 4) Persist new state
        await self.track_repository.save_all(result.active_tracks)
        if result.deleted_tracks:
            await self.track_repository.mark_deleted(result.deleted_tracks)

        return ProcessDetectionsResult(
            active_tracks=result.active_tracks,
            new_tracks=result.new_tracks,
            deleted_tracks=result.deleted_tracks,
            events=[],
        )
