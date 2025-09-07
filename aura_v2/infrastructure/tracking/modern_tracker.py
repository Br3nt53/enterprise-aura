from __future__ import annotations
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import linear_sum_assignment
from filterpy.kalman import KalmanFilter
from aura_v2.domain import (
    Detection, Track, TrackState, TrackStatus, ThreatLevel,
    Position3D, Velocity3D
)

@dataclass
class TrackingResult:
    active_tracks: List[Track]
    new_tracks: List[Track]
    deleted_tracks: List[Track]
    processing_time_ms: float

class ModernTracker:
    def __init__(self, max_age: int = 30, min_hits: int = 3, iou_threshold: float = 0.3, max_distance: float = 50.0) -> None:
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.max_distance = max_distance
        self.tracks: Dict[str, Track] = {}
        self.kalman_filters: Dict[str, KalmanFilter] = {}
        self.next_track_id = 0

    def create_state_from_detection(self, detection: Detection) -> TrackState:
        return TrackState(position=detection.position, velocity=Velocity3D())

    async def update(self, detections: List[Detection], timestamp: datetime) -> TrackingResult:
        start = time.perf_counter()
        self._predict_tracks(timestamp)
        matched, unmatched_dets, unmatched_tracks = self._associate(detections)
        for track_id, det, score in matched:
            self._update_track(track_id, det, score, timestamp)
        new_tracks: List[Track] = []
        for det in unmatched_dets:
            new_tracks.append(self._create_track(det, timestamp))
        for track_id in unmatched_tracks:
            self.tracks[track_id].mark_missed()
        deleted_tracks = self._delete_old_tracks()
        active = [t for t in self.tracks.values() if t.status != TrackStatus.DELETED]
        ms = (time.perf_counter() - start) * 1000.0
        return TrackingResult(active_tracks=active, new_tracks=new_tracks, deleted_tracks=deleted_tracks, processing_time_ms=ms)

    def _predict_tracks(self, timestamp: datetime) -> None:
        for tid, track in list(self.tracks.items()):
            if track.status == TrackStatus.DELETED:
                continue
            kf = self.kalman_filters[tid]
            dt = (timestamp - track.updated_at).total_seconds()
            if dt <= 0:
                continue
            kf.F[0, 3] = dt; kf.F[1, 4] = dt; kf.F[2, 5] = dt
            kf.predict()
            track.state = TrackState(
                position=Position3D(float(kf.x[0,0]), float(kf.x[1,0]), float(kf.x[2,0])),
                velocity=Velocity3D(float(kf.x[3,0]), float(kf.x[4,0]), float(kf.x[5,0]))
            )

    def _associate(self, detections: List[Detection]) -> Tuple[List[Tuple[str, Detection, float]], List[Detection], List[str]]:
        ids = [tid for tid, t in self.tracks.items() if t.status != TrackStatus.DELETED]
        if not ids or not detections:
            return [], detections, ids
        cost = np.zeros((len(ids), len(detections)), dtype=float)
        for i, tid in enumerate(ids):
            tr = self.tracks[tid]
            for j, det in enumerate(detections):
                cost[i, j] = tr.state.position.distance_to(det.position)
        cost[cost > self.max_distance] = 1e6
        ti, dj = linear_sum_assignment(cost)
        matched: List[Tuple[str, Detection, float]] = []
        mt, md = set(), set()
        for a, b in zip(ti, dj):
            if cost[a, b] < self.max_distance:
                matched.append((ids[a], detections[b], 1.0 / (1.0 + cost[a, b])))
                mt.add(a); md.add(b)
        unmatched_tracks = [ids[i] for i in range(len(ids)) if i not in mt]
        unmatched_dets = [detections[j] for j in range(len(detections)) if j not in md]
        return matched, unmatched_dets, unmatched_tracks

    def _update_track(self, track_id: str, detection: Detection, score: float, timestamp: datetime) -> None:
        tr = self.tracks[track_id]
        kf = self.kalman_filters[track_id]
        z = detection.position.to_array().reshape(3,1)
        kf.update(z)
        tr.state = TrackState(
            position=Position3D(float(kf.x[0,0]), float(kf.x[1,0]), float(kf.x[2,0])),
            velocity=Velocity3D(float(kf.x[3,0]), float(kf.x[4,0]), float(kf.x[5,0]))
        )
        tr.update(detection, score)
        tr.updated_at = timestamp

    def _create_track(self, detection: Detection, timestamp: datetime) -> Track:
        tid = f"track_{self.next_track_id:05d}"; self.next_track_id += 1
        kf = KalmanFilter(dim_x=6, dim_z=3)
        kf.x = np.array([[detection.position.x],[detection.position.y],[detection.position.z],[0.0],[0.0],[0.0]], dtype=float)
        kf.F = np.array([[1,0,0,1,0,0],[0,1,0,0,1,0],[0,0,1,0,0,1],[0,0,0,1,0,0],[0,0,0,0,1,0],[0,0,0,0,0,1]], dtype=float)
        kf.H = np.array([[1,0,0,0,0,0],[0,1,0,0,0,0],[0,0,1,0,0,0]], dtype=float)
        kf.R = np.eye(3)*1.0; kf.Q = np.eye(6)*0.1; kf.P = np.eye(6)*10.0
        self.kalman_filters[tid] = kf
        tr = Track(
            id=tid,
            state=TrackState(position=detection.position, velocity=Velocity3D()),
            status=TrackStatus.TENTATIVE,
            confidence=detection.confidence,
            threat_level=ThreatLevel.LOW,
            created_at=timestamp,
            updated_at=timestamp,
            hits=1,
            missed=0,
        )
        self.tracks[tid] = tr
        return tr

    def _delete_old_tracks(self) -> List[Track]:
        deleted: List[Track] = []
        to_del: List[str] = []
        for tid, tr in self.tracks.items():
            if tr.missed > self.max_age:
                tr.status = TrackStatus.DELETED
                deleted.append(tr)
                to_del.append(tid)
        for tid in to_del:
            self.tracks.pop(tid, None)
            self.kalman_filters.pop(tid, None)
        return deleted
