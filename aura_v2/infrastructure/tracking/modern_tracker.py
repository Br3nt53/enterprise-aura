# aura_v2/infrastructure/tracking/modern_tracker.py

import os
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import numpy as np
from filterpy.kalman import KalmanFilter

# Domain imports
from ...domain.entities import Detection, Track, TrackState, TrackStatus
from ...infrastructure.persistence.in_memory import InMemoryTrackRepository # Used for type hint
from ...infrastructure.persistence.mongo import MongoTrackRepository # Used for type hint


try:
    from ...domain.value_objects.velocity import Velocity3D
except Exception:
    from ...domain.entities import Velocity3D


@dataclass
class TrackingResult:
    active_tracks: List[Track]
    new_tracks: List[Track]
    deleted_tracks: List[Track]
    processing_time_ms: float = 0.0


class ModernTracker:
    def _to_dt(self, ts) -> datetime:
        if isinstance(ts, datetime):
            return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
        if isinstance(ts, str):
            t = ts.rstrip()
            if t.endswith("Z"):
                t = t[:-1] + "+00:00"
            return datetime.fromisoformat(t)
        raise TypeError("Unsupported timestamp type")

    """Minimal, test-oriented multi-sensor tracker with timing metrics."""

    def __init__(
        self,
        track_repository: InMemoryTrackRepository | MongoTrackRepository,
        max_distance: float = 50.0,
        max_missed: int = 2
    ) -> None:
        self.track_repository = track_repository
        self.kalman_filters: Dict[str, KalmanFilter] = {}
        self._id_counter: int = 0
        self.max_distance = float(max_distance)
        self.max_missed = int(max_missed)
        self.stale_after_sec = float(os.getenv("AURA_TRACK_STALE_SEC", "5.0"))
        self._frame_timestamp = None
        self._last_obs: Dict[str, datetime] = {}

    async def update(self, detections: List[Detection], timestamp: datetime) -> TrackingResult:
        start_time = time.time()
        self._frame_timestamp = self._to_dt(timestamp)

        current_tracks = await self.track_repository.list()

        # 1) Predict all current tracks to this timestamp
        for t in current_tracks:
            self.predict_track(t, timestamp)

        # 2) Associate detections to tracks (greedy nearest-neighbor)
        matched, unmatched_dets, unmatched_tracks = self._associate(detections, current_tracks)

        # 3) Update matched tracks
        for track, det, score in matched:
            self._update_track(track, det, score, timestamp)
            await self.track_repository.save(track)

        # 4) Spawn new tracks for unmatched detections
        new_tracks: List[Track] = []
        for det in unmatched_dets:
            nt = self._new_track_from_detection(det, self._frame_timestamp)
            await self.track_repository.save(nt)
            self._last_obs[nt.id] = self._frame_timestamp
            new_tracks.append(nt)

        # 5) Keep unmatched tracks alive; increment missed
        for t in unmatched_tracks:
            t.missed = getattr(t, "missed", 0) + 1
            await self.track_repository.save(t)

        # 6) Prune old tracks
        deleted_tracks = await self._prune()

        processing_time = (time.time() - start_time) * 1000
        active_tracks = [t for t in await self.track_repository.list() if t.status != TrackStatus.DELETED]

        return TrackingResult(
            active_tracks=active_tracks,
            new_tracks=new_tracks,
            deleted_tracks=deleted_tracks,
            processing_time_ms=processing_time,
        )


    def predict_track(self, track: Track, timestamp: datetime) -> None:
        """Advance a single track's KF to 'timestamp' and rebuild frozen state."""
        if track.id not in self.kalman_filters:
            self._init_kf(track)

        kf = self.kalman_filters[track.id]
        dt = (timestamp - track.updated_at).total_seconds()
        if dt <= 0:
            return

        kf.F[0, 3] = dt
        kf.F[1, 4] = dt
        kf.F[2, 5] = dt
        kf.predict()

        pos = replace(
            track.state.position,
            x=float(kf.x[0, 0]),
            y=float(kf.x[1, 0]),
            z=float(kf.x[2, 0]),
        )
        vel0 = track.state.velocity or Velocity3D(0.0, 0.0, 0.0)
        vel = replace(
            vel0,
            vx=float(kf.x[3, 0]),
            vy=float(kf.x[4, 0]),
            vz=float(kf.x[5, 0]),
        )
        track.state = replace(track.state, position=pos, velocity=vel)


    def _update_track(
        self, track: Track, detection: Detection, score: float, timestamp: datetime
    ) -> None:
        """KF measurement update and immutable state rebuild."""
        kf = self.kalman_filters[track.id]
        z = np.array(
            [detection.position.x, detection.position.y, detection.position.z],
            dtype=float,
        ).reshape(3, 1)
        kf.update(z)

        pos = replace(
            track.state.position,
            x=float(kf.x[0, 0]),
            y=float(kf.x[1, 0]),
            z=float(kf.x[2, 0]),
        )
        vel0 = track.state.velocity or Velocity3D(0.0, 0.0, 0.0)
        vel = replace(
            vel0,
            vx=float(kf.x[3, 0]),
            vy=float(kf.x[4, 0]),
            vz=float(kf.x[5, 0]),
        )
        track.state = replace(track.state, position=pos, velocity=vel)

        if hasattr(track, "update"):
            track.update(detection, score)
        track.updated_at = self._frame_timestamp
        self._last_obs[track.id] = self._frame_timestamp

        track.missed = 0
        track.hits = getattr(track, "hits", 0) + 1


    def _associate(
        self, detections: List[Detection], live_tracks: List[Track]
    ) -> Tuple[List[Tuple[Track, Detection, float]], List[Detection], List[Track]]:
        """Greedy nearest-neighbor association within max_distance."""
        if not live_tracks:
            return [], detections, []

        matched: List[Tuple[Track, Detection, float]] = []
        used_tracks: set[int] = set()
        used_dets: set[int] = set()

        for j, det in enumerate(detections):
            best_i = -1
            best_dist = float("inf")
            for i, tr in enumerate(live_tracks):
                if i in used_tracks:
                    continue
                dist = self._euclidean(tr.state.position, det.position)
                if dist < best_dist:
                    best_dist = dist
                    best_i = i
            if best_i >= 0 and best_dist <= self.max_distance:
                matched.append((live_tracks[best_i], det, 1.0 / (1.0 + best_dist)))
                used_tracks.add(best_i)
                used_dets.add(j)

        unmatched_dets = [d for j, d in enumerate(detections) if j not in used_dets]
        unmatched_tracks = [t for i, t in enumerate(live_tracks) if i not in used_tracks]
        return matched, unmatched_dets, unmatched_tracks


    def _new_track_from_detection(self, detection: Detection, now: datetime) -> Track:
        track_id = self._next_track_id()
        state = TrackState(
            position=detection.position,
            velocity=Velocity3D(0.0, 0.0, 0.0),
        )
        track = Track(
            id=track_id,
            state=state,
            status=TrackStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            hits=1,
            missed=0,
        )
        self._init_kf(track)
        return track


    def _init_kf(self, track: Track) -> None:
        kf = KalmanFilter(dim_x=6, dim_z=3)
        kf.F = np.eye(6, dtype=float)
        kf.H = np.hstack([np.eye(3), np.zeros((3, 3))]).astype(float)
        kf.P = np.eye(6, dtype=float) * 10.0
        kf.R = np.eye(3, dtype=float) * 0.5
        kf.Q = np.eye(6, dtype=float) * 0.01
        vx = track.state.velocity.vx if track.state.velocity else 0.0
        vy = track.state.velocity.vy if track.state.velocity else 0.0
        vz = track.state.velocity.vz if track.state.velocity else 0.0
        kf.x = np.array(
            [
                [float(track.state.position.x)],
                [float(track.state.position.y)],
                [float(track.state.position.z)],
                [float(vx)],
                [float(vy)],
                [float(vz)],
            ],
            dtype=float,
        )
        self.kalman_filters[track.id] = kf


    async def _prune(self) -> List[Track]:
        deleted: List[Track] = []
        ttl = getattr(self, "stale_after_sec", 5.0)
        ts = getattr(self, "_frame_timestamp", None)
        
        current_tracks = await self.track_repository.list()
        for t in current_tracks:
            too_old = False
            if ts is not None and getattr(t, "updated_at", None) is not None and ttl > 0:
                try:
                    age = (ts - t.updated_at).total_seconds()
                    too_old = age > ttl
                except Exception:
                    too_old = False
            if t.missed > self.max_missed or too_old:
                t.status = TrackStatus.DELETED
                deleted.append(t)
                await self.track_repository.delete(t.id)
                self.kalman_filters.pop(t.id, None)
        return deleted


    def _next_track_id(self) -> str:
        tid = f"track_{self._id_counter:05d}"
        self._id_counter += 1
        return tid

    @staticmethod
    def _euclidean(a: Any, b: Any) -> float:
        dx = float(a.x) - float(b.x)
        dy = float(a.y) - float(b.y)
        dz = float(a.z) - float(b.z)
        return float(np.sqrt(dx * dx + dy * dy + dz * dz))