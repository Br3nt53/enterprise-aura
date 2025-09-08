# aura_v2/domain/services/association.py
from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
from scipy.optimize import linear_sum_assignment
from ..entities import Detection, Track


class AssociationStrategy(ABC):
    """Abstract base class for association strategies."""

    @abstractmethod
    def associate(
        self, tracks: List[Track], detections: List[Detection]
    ) -> List[Tuple[Track, Detection, float]]:
        """Associates detections to tracks."""
        pass


class GNN_AssociationStrategy(AssociationStrategy):
    """Global Nearest Neighbor association strategy."""

    def __init__(self, max_distance: float = 50.0):
        self.max_distance = max_distance

    def associate(
        self, tracks: List[Track], detections: List[Detection]
    ) -> List[Tuple[Track, Detection, float]]:
        """
        Associates detections to tracks using Global Nearest Neighbor (GNN) algorithm.
        This is a concrete implementation.
        """
        if not tracks or not detections:
            return []

        # Create a cost matrix
        cost_matrix = np.full((len(tracks), len(detections)), self.max_distance + 1.0)
        for i, track in enumerate(tracks):
            for j, detection in enumerate(detections):
                distance = np.linalg.norm(
                    track.state.position.to_array() - detection.position.to_array()
                )
                if distance < self.max_distance:
                    cost_matrix[i, j] = distance

        # Use the Hungarian algorithm to find the optimal assignment
        track_indices, detection_indices = linear_sum_assignment(cost_matrix)

        associations = []
        for track_idx, det_idx in zip(track_indices, detection_indices):
            if cost_matrix[track_idx, det_idx] <= self.max_distance:
                track = tracks[track_idx]
                detection = detections[det_idx]
                # Score can be inverse of distance, or simply 1.0
                score = 1.0 / (1.0 + cost_matrix[track_idx, det_idx])
                associations.append((track, detection, score))

        return associations
