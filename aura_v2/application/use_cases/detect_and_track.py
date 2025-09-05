# aura_v2/application/use_cases/detect_and_track.py
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import asyncio

from ...domain.entities import Track, Detection, ThreatLevel
from ...domain.services import MultiSensorFusion
from ...domain.events import (
    TrackCreated, TrackUpdated, TrackDeleted,
    ThreatDetected, CollisionWarning
)
from ...infrastructure.tracking import ModernTracker

@dataclass
class DetectAndTrackCommand:
    """Command to process sensor data and maintain tracks"""
    radar_data: List[Detection]
    lidar_data: List[Detection]
    camera_data: List[Detection]
    timestamp: datetime

@dataclass
class TrackingResult:
    """Result of tracking operation"""
    active_tracks: List[Track]
    new_tracks: List[Track]
    deleted_tracks: List[Track]
    threats: List[ThreatAssessment]
    events: List[DomainEvent]

class DetectAndTrackUseCase:
    """
    Main use case: Process multi-sensor data to maintain tracks
    and generate actionable intelligence
    """
    
    def __init__(self,
                 tracker: ModernTracker,
                 fusion_service: MultiSensorFusion,
                 threat_analyzer: ThreatAnalyzer,
                 collision_predictor: CollisionPredictor,
                 event_publisher: EventPublisher):
        self.tracker = tracker
        self.fusion = fusion_service
        self.threat_analyzer = threat_analyzer
        self.collision_predictor = collision_predictor
        self.events = event_publisher
    
    async def execute(self, command: DetectAndTrackCommand) -> TrackingResult:
        """
        Main tracking pipeline:
        1. Fuse multi-sensor data
        2. Update tracks
        3. Assess threats
        4. Predict collisions
        5. Generate alerts
        """
        
        # 1. Sensor Fusion - Combine all sensor data
        fused_detections = await self._fuse_sensors(
            command.radar_data,
            command.lidar_data, 
            command.camera_data
        )
        
        # 2. Track Association & Update
        tracking_result = await self.tracker.update(
            fused_detections,
            command.timestamp
        )
        
        # 3. Threat Assessment
        threats = []
        for track in tracking_result.active_tracks:
            threat_level = self.threat_analyzer.assess(track)
            
            if threat_level >= ThreatLevel.HIGH:
                threat = ThreatAssessment(
                    track=track,
                    threat_level=threat_level,
                    confidence=track.confidence.value,
                    recommended_action=self._get_recommended_action(threat_level)
                )
                threats.append(threat)
                
                # Publish threat event
                await self.events.publish(ThreatDetected(
                    track_id=track.id,
                    threat_level=threat_level,
                    timestamp=command.timestamp
                ))
        
        # 4. Collision Prediction
        collision_risks = self.collision_predictor.predict(
            tracking_result.active_tracks,
            time_horizon=10.0  # seconds
        )
        
        for risk in collision_risks:
            if risk.probability > 0.7:
                await self.events.publish(CollisionWarning(
                    track1_id=risk.track1.id,
                    track2_id=risk.track2.id,
                    time_to_collision=risk.time_to_collision,
                    probability=risk.probability,
                    timestamp=command.timestamp
                ))
        
        # 5. Generate events for new/updated/deleted tracks
        events = []
        for track in tracking_result.new_tracks:
            events.append(TrackCreated(
                track_id=track.id,
                position=track.state.position,
                timestamp=command.timestamp
            ))
        
        return TrackingResult(
            active_tracks=tracking_result.active_tracks,
            new_tracks=tracking_result.new_tracks,
            deleted_tracks=tracking_result.deleted_tracks,
            threats=threats,
            events=events
        )
    
    async def _fuse_sensors(self, 
                           radar: List[Detection],
                           lidar: List[Detection],
                           camera: List[Detection]) -> List[Detection]:
        """Intelligent sensor fusion with confidence weighting"""
        
        # Group detections by proximity
        clusters = self._cluster_detections(radar + lidar + camera)
        
        fused = []
        for cluster in clusters:
            # Fuse cluster into single detection
            fused_detection = self.fusion.fuse_cluster(cluster)
            fused.append(fused_detection)
        
        return fused