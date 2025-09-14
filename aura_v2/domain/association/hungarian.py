from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass
class AssociationResult:
    is_match: bool
    reading: "SensorReading"
    track: Optional["TrackState"] = None


class HungarianAssociation:
    def __init__(self, max_distance: float = 15.0):
        self.max_distance = max_distance

    def associate(
        self, readings: Sequence["SensorReading"], tracks: Sequence["TrackState"]
    ) -> list[AssociationResult]:
        # Naive placeholder (replace with real Hungarian algorithm)
        results: list[AssociationResult] = []
        unused_tracks = list(tracks)
        for r in readings:
            best = None
            best_dist = self.max_distance
            for t in unused_tracks:
                d = math.dist((r.x, r.y), (t.state.x, t.state.y))
                if d < best_dist:
                    best = t
                    best_dist = d
            if best:
                unused_tracks.remove(best)
                results.append(AssociationResult(is_match=True, reading=r, track=best))
            else:
                results.append(AssociationResult(is_match=False, reading=r))
        return results
