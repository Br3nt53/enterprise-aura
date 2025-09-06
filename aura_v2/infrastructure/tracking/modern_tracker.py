# aura_v2/infrastructure/tracking/modern_tracker.py
"""
Modern multi-object tracker with Kalman filtering and Hungarian association
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter

from ...domain.entities import Track, Detection, TrackStatus, ThreatLevel
from ...domain.entities.track import TrackState
from ...domain.value_objects import Position3D, Velocity3D, Confidence, TrackID


@dataclass
class TrackingResult:
    """Result of a tracking update"""
    active_tracks: List[Track]
    new_tracks: List[Track] 
    deleted_tracks: List[Track]
    processing_time_ms: float = 0.0


class ModernTracker:
    """
    State-of-the-art multi-object tracker using:
    - Kalman filtering for state estimation
    - Hungarian algorithm for data association
    - Track lifecycle management
    """
    
    def __init__(self,
                 max_age: int = 30,
                 min_hits: int = 3,
                 iou_threshold: float = 0.3,
                 max_distance: float = 50.0):
        
        self.max_age = max_age  # Maximum frames to keep track without detection
        self.min_hits = min_hits  # Minimum hits to confirm track
        self.iou_threshold = iou_threshold  # For IoU-based association
        self.max_distance = max_distance  # Maximum distance for association
        
        self.tracks: Dict[TrackID, Track] = {}
        self.kalman_filters: Dict[TrackID, KalmanFilter] = {}
        self.next_track_id = 0
        
    async def update(self, 
                    detections: List[Detection],
                    timestamp: datetime) -> TrackingResult:
        """
        Main tracking update step
        """
        import time
        start_time = time.perf_counter()
        
        # 1. Predict existing tracks to current timestamp
        self._predict_tracks(timestamp)
        
        # 2. Associate detections to predicted tracks
        matched, unmatched_dets, unmatched_tracks = self._associate(detections)
        
        # 3. Update matched tracks
        for track_id, detection, score in matched:
            self._update_track(track_id, detection, score, timestamp)
        
        # 4. Create new tracks for unmatched detections
        new_tracks = []
        for detection in unmatched_dets:
            new_track = self._create_track(detection, timestamp)
            new_tracks.append(new_track)
        
        # 5. Handle unmatched tracks (mark as missed)
        for track_id in unmatched_tracks:
            self.tracks[track_id].mark_missed()
        
        # 6. Delete old tracks
        deleted_tracks = self._delete_old_tracks()
        
        # 7. Prepare result
        active_tracks = [t for t in self.tracks.values() 
                        if t.status != TrackStatus.DELETED]
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        return TrackingResult(
            active_tracks=active_tracks,
            new_tracks=new_tracks,
            deleted_tracks=deleted_tracks,
            processing_time_ms=processing_time
        )
    
    def _predict_tracks(self, timestamp: datetime) -> None:
        """Predict all tracks to current timestamp using Kalman filter"""
        
        for track_id, track in self.tracks.items():
            if track.status == TrackStatus.DELETED:
                continue
                
            kf = self.kalman_filters[track_id]
            
            # Calculate time delta
            dt = (timestamp - track.updated_at).total_seconds()
            if dt <= 0:
                continue
            
            # Update state transition matrix with dt
            kf.F[0, 3] = dt  # x position from x velocity
            kf.F[1, 4] = dt  # y position from y velocity
            kf.F[2, 5] = dt  # z position from z velocity
            
            # Predict
            kf.predict()
            
            # Update track state with prediction
            track.state.position = Position3D(
                x=kf.x[0, 0],
                y=kf.x[1, 0], 
                z=kf.x[2, 0]
            )
            track.state.velocity = Velocity3D(
                vx=kf.x[3, 0],
                vy=kf.x[4, 0],
                vz=kf.x[5, 0]
            )
    
    def _associate(self, 
                  detections: List[Detection]
                  ) -> Tuple[List[Tuple[TrackID, Detection, float]], 
                           List[Detection], 
                           List[TrackID]]:
        """
        Associate detections to tracks using Hungarian algorithm
        Returns: (matched, unmatched_detections, unmatched_tracks)
        """
        
        active_track_ids = [tid for tid, t in self.tracks.items() 
                           if t.status != TrackStatus.DELETED]
        
        if not active_track_ids or not detections:
            return [], detections, active_track_ids
        
        # Build cost matrix (distance-based)
        cost_matrix = np.zeros((len(active_track_ids), len(detections)))
        
        for i, track_id in enumerate(active_track_ids):
            track = self.tracks[track_id]
            for j, detection in enumerate(detections):
                # Euclidean distance
                dist = track.state.position.distance_to(detection.position)
                cost_matrix[i, j] = dist
        
        # Apply gating (max distance threshold)
        cost_matrix[cost_matrix > self.max_distance] = 1e6
        
        # Hungarian algorithm
        track_indices, det_indices = linear_sum_assignment(cost_matrix)
        
        # Build matches
        matched = []
        for t_idx, d_idx in zip(track_indices, det_indices):
            if cost_matrix[t_idx, d_idx] < self.max_distance:
                track_id = active_track_ids[t_idx]
                detection = detections[d_idx]
                score = 1.0 / (1.0 + cost_matrix[t_idx, d_idx])  # Convert distance to score
                matched.append((track_id, detection, score))
        
        # Find unmatched
        matched_track_indices = {t_idx for t_idx, _ in zip(track_indices, det_indices)
                                if cost_matrix[t_idx, det_indices[list(track_indices).index(t_idx)]] < self.max_distance}
        matched_det_indices = {d_idx for _, d_idx in zip(track_indices, det_indices)
                              if cost_matrix[track_indices[list(det_indices).index(d_idx)], d_idx] < self.max_distance}
        
        unmatched_tracks = [active_track_ids[i] for i in range(len(active_track_ids))
                           if i not in matched_track_indices]
        unmatched_dets = [detections[j] for j in range(len(detections))
                         if j not in matched_det_indices]
        
        return matched, unmatched_dets, unmatched_tracks
    
    def _update_track(self, 
                     track_id: TrackID,
                     detection: Detection,
                     score: float,
                     timestamp: datetime) -> None:
        """Update track with matched detection using Kalman filter"""
        
        track = self.tracks[track_id]
        kf = self.kalman_filters[track_id]
        
        # Kalman update
        z = np.array([[detection.position.x],
                     [detection.position.y],
                     [detection.position.z]])
        kf.update(z)
        
        # Update track state from Kalman filter
        track.state.position = Position3D(
            x=kf.x[0, 0],
            y=kf.x[1, 0],
            z=kf.x[2, 0]
        )
        track.state.velocity = Velocity3D(
            vx=kf.x[3, 0],
            vy=kf.x[4, 0],
            vz=kf.x[5, 0]
        )
        
        # Update track metadata
        track.update(detection, score)
        track.updated_at = timestamp
        
        # Assess threat level
        track.threat_level = track.assess_threat()
    
    def _create_track(self, 
                     detection: Detection,
                     timestamp: datetime) -> Track:
        """Create new track from unmatched detection"""
        
        track_id = TrackID(f"track_{self.next_track_id:05d}")
        self.next_track_id += 1
        
        # Initialize Kalman filter (constant velocity model)
        kf = KalmanFilter(dim_x=6, dim_z=3)  # 6 state dims, 3 measurement dims
        
        # State: [x, y, z, vx, vy, vz]
        kf.x = np.array([[detection.position.x],
                        [detection.position.y],
                        [detection.position.z],
                        [0.0],  # Initial velocity unknown
                        [0.0],
                        [0.0]])
        
        # State transition matrix (will be updated with dt)
        kf.F = np.array([[1, 0, 0, 1, 0, 0],
                        [0, 1, 0, 0, 1, 0],
                        [0, 0, 1, 0, 0, 1],
                        [0, 0, 0, 1, 0, 0],
                        [0, 0, 0, 0, 1, 0],
                        [0, 0, 0, 0, 0, 1]])
        
        # Measurement matrix (position only)
        kf.H = np.array([[1, 0, 0, 0, 0, 0],
                        [0, 1, 0, 0, 0, 0],
                        [0, 0, 1, 0, 0, 0]])
        
        # Measurement noise
        kf.R = np.eye(3) * 1.0  # 1 meter std dev
        
        # Process noise
        kf.Q = np.eye(6) * 0.1
        
        # Initial uncertainty
        kf.P = np.eye(6) * 10.0
        
        self.kalman_filters[track_id] = kf
        
        # Create track
        track = Track(
            id=track_id,
            state=TrackState(
                position=detection.position,
                velocity=Velocity3D(vx=0, vy=0, vz=0)
            ),
            status=TrackStatus.TENTATIVE,
            confidence=detection.confidence,
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self.tracks[track_id] = track
        return track
    
    def _delete_old_tracks(self) -> List[Track]:
        """Delete tracks that have been missed for too long"""
        
        deleted = []
        to_delete = []
        
        for track_id, track in self.tracks.items():
            if track.time_since_update > self.max_age:
                track.status = TrackStatus.DELETED
                deleted.append(track)
                to_delete.append(track_id)
        
        # Clean up
        for track_id in to_delete:
            del self.tracks[track_id]
            del self.kalman_filters[track_id]
        
        return deleted