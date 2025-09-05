# aura_v2/application/use_cases/process_detections.py
from dataclasses import dataclass
from typing import List, Optional
from ...domain.entities import Detection, Track
from ...domain.services import AssociationStrategy
from ...domain.events import TrackCreated, TrackUpdated, TrackDeleted

@dataclass
class ProcessDetectionsCommand:
    """Command to process new detections"""
    detections: List[Detection]
    timestamp: datetime

@dataclass
class ProcessDetectionsResult:
    """Result of processing detections"""
    active_tracks: List[Track]
    new_tracks: List[Track]
    deleted_tracks: List[Track]
    events: List[DomainEvent]

class ProcessDetectionsUseCase:
    """Application service for processing detections"""
    
    def __init__(
        self,
        track_repository: 'TrackRepository',
        association_service: AssociationStrategy,
        event_publisher: 'EventPublisher',
        track_manager: 'TrackManager'
    ):
        self.track_repository = track_repository
        self.association_service = association_service
        self.event_publisher = event_publisher
        self.track_manager = track_manager
    
    async def execute(self, command: ProcessDetectionsCommand) -> ProcessDetectionsResult:
        """Process detections and update tracks"""
        
        # 1. Get active tracks
        active_tracks = await self.track_repository.get_active_tracks()
        
        # 2. Predict tracks to current time
        predicted_tracks = [
            self.track_manager.predict_track(track, command.timestamp)
            for track in active_tracks
        ]
        
        # 3. Associate detections to tracks
        associations = self.association_service.associate(
            predicted_tracks, 
            command.detections
        )
        
        # 4. Process associations
        events = []
        new_tracks = []
        updated_tracks = []
        
        for track, detection, score in associations:
            if track is None and detection is not None:
                # Create new track
                new_track = self.track_manager.create_track(detection)
                new_tracks.append(new_track)
                events.append(TrackCreated(
                    occurred_at=command.timestamp,
                    aggregate_id=str(new_track.id),
                    track_id=new_track.id,
                    initial_detection=detection
                ))
            elif track is not None and detection is not None:
                # Update existing track
                track.update(detection, score)
                updated_tracks.append(track)
                events.append(TrackUpdated(
                    occurred_at=command.timestamp,
                    aggregate_id=str(track.id),
                    track_id=track.id,
                    detection=detection,
                    confidence=track.confidence
                ))
        
        # 5. Handle track deletion
        deleted_tracks = self.track_manager.check_track_deletion(
            active_tracks, 
            command.timestamp
        )
        for track in deleted_tracks:
            events.append(TrackDeleted(
                occurred_at=command.timestamp,
                aggregate_id=str(track.id),
                track_id=track.id,
                reason="timeout"
            ))
        
        # 6. Save changes
        await self.track_repository.save_all(new_tracks + updated_tracks)
        await self.track_repository.mark_deleted(deleted_tracks)
        
        # 7. Publish events
        for event in events:
            await self.event_publisher.publish(event)
        
        return ProcessDetectionsResult(
            active_tracks=updated_tracks,
            new_tracks=new_tracks,
            deleted_tracks=deleted_tracks,
            events=events
        )