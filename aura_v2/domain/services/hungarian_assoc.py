from __future__ import annotations
from typing import List, Tuple
import math
import numpy as np
from scipy.optimize import linear_sum_assignment

# Minimal protocol for Track/Detection used here:
#  - Track: .id (str), .state.position -> tuple[float,float] or (x,y,...) indexable
#  - Detection: .id (str), .position -> tuple[float,float] or (x,y,...) indexable

def _euclidean(a, b) -> float:
    ax, ay = a[0], a[1]
    bx, by = b[0], b[1]
    dx, dy = ax - bx, ay - by
    return math.hypot(dx, dy)

class HungarianAssociationStrategy:
    def __init__(self, max_distance: float = 5.0) -> None:
        self.max_distance = max_distance

    def associate(
        self,
        tracks: List[object],
        detections: List[object],
    ) -> Tuple[List[Tuple[object, object]], List[object], List[object]]:
        if not tracks or not detections:
            return [], list(detections), list(tracks)

        n_t, n_d = len(tracks), len(detections)
        cost = np.zeros((n_t, n_d), dtype=np.float32)
        for i, tr in enumerate(tracks):
            tp = tr.state.position
            for j, det in enumerate(detections):
                dp = det.position
                d = _euclidean(tp, dp)
                cost[i, j] = d if d <= self.max_distance else 1e6  # effectively forbid

        rows, cols = linear_sum_assignment(cost)
        matched, used_t, used_d = [], set(), set()
        for i, j in zip(rows, cols):
            if cost[i, j] < 1e6:
                matched.append((tracks[i], detections[j]))
                used_t.add(i)
                used_d.add(j)

        unmatched_tracks = [t for i, t in enumerate(tracks) if i not in used_t]
        unmatched_dets = [d for j, d in enumerate(detections) if j not in used_d]
        return matched, unmatched_dets, unmatched_tracks
