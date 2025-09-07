"""
Modern object tracker using Kalman filtering and Hungarian association.

This tracker maintains a set of tracks and updates them frame‑by‑frame
based on incoming detections.  It uses a constant‑velocity Kalman filter
to predict track positions, applies the Hungarian algorithm to associate
detections with existing tracks using Euclidean distance, and manages
track lifecycle through tentative, active, lost and deleted states.

The tracker is designed to be independent of any machine‑learning
libraries; it operates purely on the value objects defined in
``aura_v2.domain``.  It can be used on both macOS and Windows without
hardware dependencies.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np  # type: ignore
from scipy.optimize import linear_sum_assignment  # type: ignore
from filterpy.kalman import KalmanFilter  # type: ignore

from aura_v2.domain import (
    Detection,
    Track,
    TrackState,
    TrackStatus,
    ThreatLevel,
    Position3D,
    Velocity3D,
    Confidence,
)

@dataclass
class TrackingResult:
    """Result returned by ``ModernTracker.update``."""
    active_tracks: List[Track]
    new_tracks: List[Track]
    deleted_tracks: List[Track]
    processing_time_ms: float

class ModernTracker:
    """State‑of‑the‑art multi‑object tracker with Kalman filtering."""

    def __init__(
        self,
        max_age: int = 30,
        min_hits: int = 3,
        iou_threshold: float = 0.3,
        max_distance: float = 50.0,
    ) -> None:
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.max_distance = max_distance
        self.tracks: Dict[str, Track] = {}
        self.kalman_filters: Dict[str, KalmanFilter] = {}
        self.next_track_id: int = 0

    def create_state_from_detection(self, detection: Detection) -> TrackState:
        """Create an initial track state from a detection."""
        return TrackState(position=detection.position, velocity=Velocity3D())

    async def update(self, detections: List[Detection], timestamp: datetime) -> TrackingResult:
        """Update the tracker given detections from the current frame."""
        start_time = time.perf_counter()
        # 1. Predict all tracks to current timestamp
        self._predict_tracks(timestamp)
        # 2. Associate detections to tracks
        matched, unmatched_dets, unmatched_tracks = self._associate(detections)
        # 3. Update matched tracks
        for track_id, detection, score in matched:
            self._update_track(track_id, detection, score, timestamp)
        # 4. Create new tracks for unmatched detections
        new_tracks: List[Track] = []
        for det in unmatched_dets:
            new_track = self._create_track(det, timestamp)
            new_tracks.append(new_track)
        # 5. Mark unmatched tracks as missed
        for track_id in unmatched_tracks:
            self.tracks[track_id].mark_missed()
        # 6. Delete old tracks
        deleted_tracks = self._delete_old_tracks()
        # 7. Prepare result
        active_tracks = [t for t in self.tracks.values() if t.status != TrackStatus.DELETED]
        processing_time_ms = (time.perf_counter() - start_time) * 1000.0
        return TrackingResult(
            active_tracks=active_tracks,
            new_tracks=new_tracks,
            deleted_tracks=deleted_tracks,
            processing_time_ms=processing_time_ms,
        )

    def _predict_tracks(self, timestamp: datetime) -> None:
        """Predict each track's state forward to the current timestamp using its Kalman filter."""
        for track_id, track in list(self.tracks.items()):
            if track.status == TrackStatus.DELETED:
                continue
            kf = self.kalman_filters[track_id]
            dt = (timestamp - track.updated_at).total_seconds()
            if dt <= 0:
                continue
            kf.F[0, 3] = dt
            kf.F[1, 4] = dt
            kf.F[2, 5] = dt
            kf.predict()
            track.state = TrackState(
                position=Position3D(
                    x=float(kf.x[0, 0]), y=float(kf.x[1, 0]), z=float(kf.x[2, 0])
                ),
                velocity=Velocity3D(
                    vx=float(kf.x[3, 0]), vy=float(kf.x[4, 0]), vz=float(kf.x[5, 0])
                ),
            )

    def _associate(
        self, detections: List[Detection]
    ) -> Tuple[List[Tuple[str, Detection, float]], List[Detection], List[str]]:
        """Associate detections to existing tracks using Hungarian algorithm."""
        active_track_ids = [tid for tid, t in self.tracks.items() if t.status != TrackStatus.DELETED]
        if not active_track_ids or not detections:
            return [], detections, active_track_ids
        cost_matrix = np.zeros((len(active_track_ids), len(detections)), dtype=float)
        for i, track_id in enumerate(active_track_ids):
            track = self.tracks[track_id]
            for j, det in enumerate(detections):
                dist = track.state.position.distance_to(det.position)
                cost_matrix[i, j] = dist
        cost_matrix[cost_matrix > self.max_distance] = 1e6
        track_indices, det_indices = linear_sum_assignment(cost_matrix)
        matched: List[Tuple[str, Detection, float]] = []
        matched_track_indices: set[int] = set()
        matched_det_indices: set[int] = set()
        for ti, dj in zip(track_indices, det_indices):
            if cost_matrix[ti, dj] < self.max_distance:
                track_id = active_track_ids[ti]
                detection = detections[dj]
                score = 1.0 / (1.0 + cost_matrix[ti, dj])
                matched.append((track_id, detection, score))
                matched_track_indices.add(ti)
                matched_det_indices.add(dj)
        unmatched_tracks = [active_track_ids[i] for i in range(len(active_track_ids)) if i not in matched_track_indices]
        unmatched_dets = [detections[j] for j in range(len(detections)) if j not in matched_det_indices]
        return matched, unmatched_dets, unmatched_tracks

    def _update_track(
        self, track_id: str, detection: Detection, score: float, timestamp: datetime
    ) -> None:
        """Update a matched track given a detection and similarity score."""
        track = self.tracks[track_id]
        kf = self.kalman_filters[track_id]
        z = detection.position.to_array().reshape(3, 1)
        kf.update(z)
        track.state = TrackState(
            position=Position3D(
                x=float(kf.x[0, 0]), y=float(kf.x[1, 0]), z=float(kf.x[2, 0])
            ),
            velocity=Velocity3D(
                vx=float(kf.x[3, 0]), vy=float(kf.x[4, 0]), vz=float(kf.x[5, 0])
            ),
        )
        track.update(detection, score)
        track.updated_at = timestamp

    def _create_track(self, detection: Detection, timestamp: datetime) -> Track:
        """Spawn a new track from an unmatched detection."""
        track_id = f"track_{self.next_track_id:05d}"
        self.next_track_id += 1
        kf = KalmanFilter(dim_x=6, dim_z=3)
        kf.x = np.array(
            [
                [detection.position.x],
                [detection.position.y],
                [detection.position.z],
                [0.0],
                [0.0],
                [0.0],
            ],
            dtype=float,
        )
        kf.F = np.array(
            [
                [1, 0, 0, 1, 0, 0],
                [0, 1, 0, 0, 1, 0],
                [0, 0, 1, 0, 0, 1],
                [0, 0, 0, 1, 0, 0],
                [0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1],
            ],
            dtype=float,
        )
        kf.H = np.array(
            [
                [1, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0],
            ],
            dtype=float,
        )
        kf.R = np.eye(3) * 1.0
        kf.Q = np.eye(6) * 0.1
        kf.P = np.eye(6) * 10.0
        self.kalman_filters[track_id] = kf
        track = Track(
            id=track_id,
            state=TrackState(position=detection.position, velocity=Velocity3D()),
            status=TrackStatus.TENTATIVE,
            confidence=detection.confidence,
            threat_level=ThreatLevel.LOW,
            created_at=timestamp,
            updated_at=timestamp,
            hits=1,
            missed=0,
        )
        self.tracks[track_id] = track
        return track

    def _delete_old_tracks(self) -> List[Track]:
        """Delete tracks that have been missed for too long."""
        deleted: List[Track] = []
        to_delete: List[str] = []
        for track_id, track in self.tracks.items():
            if track.missed > self.max_age:
                track.status = TrackStatus.DELETED
                deleted.append(track)
                to_delete.append(track_id)
        for track_id in to_delete:
            self.tracks.pop(track_id, None)
            self.kalman_filters.pop(track_id, None)
        return deleted
