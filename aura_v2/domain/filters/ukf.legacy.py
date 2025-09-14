from __future__ import annotations

from aura_v2.domain.tracking.track_state import TrackState


class UnscentedKalmanFilter:
    def __init__(self, process_var: float = 1.0, meas_var: float = 1.0):
        self.process_var = process_var
        self.meas_var = meas_var

    def predict(self, track: TrackState) -> None:
        # Placeholder constant velocity prediction
        dt = track.delta_t()
        track.state.x += track.state.vx * dt
        track.state.y += track.state.vy * dt
        track.state.P = track.state.P + self.process_var

    def update(self, track: TrackState, reading: object) -> None:
        # Simplified update
        k = track.state.P / (track.state.P + self.meas_var)
        track.state.x += k * (reading.x - track.state.x)
        track.state.y += k * (reading.y - track.state.y)
        track.state.P = (1 - k) * track.state.P
        track.touch()
