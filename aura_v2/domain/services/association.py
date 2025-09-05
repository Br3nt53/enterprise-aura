# aura_v2/domain/services/association.py
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
import numpy as np

class AssociationStrategy(ABC):
    """Domain service interface for data association"""
    
    @abstractmethod
    def associate(
        self, 
        tracks: List[Track], 
        detections: List[Detection]
    ) -> List[Tuple[Optional[Track], Optional[Detection], float]]:
        """
        Returns list of (track, detection, score) associations.
        None track means new track, None detection means missed detection.
        """
        pass

class HungarianAssociation(AssociationStrategy):
    """Optimal assignment using Hungarian algorithm"""
    
    def __init__(self, gate_threshold: float = 2.0):
        self.gate_threshold = gate_threshold
    
    def associate(
        self, 
        tracks: List[Track], 
        detections: List[Detection]
    ) -> List[Tuple[Optional[Track], Optional[Detection], float]]:
        if not tracks or not detections:
            return self._handle_empty_case(tracks, detections)
        
        # Build cost matrix
        cost_matrix = self._build_cost_matrix(tracks, detections)
        
        # Apply gating
        cost_matrix[cost_matrix > self.gate_threshold] = np.inf
        
        # Solve assignment problem
        from scipy.optimize import linear_sum_assignment
        track_indices, det_indices = linear_sum_assignment(cost_matrix)
        
        # Build associations
        associations = []
        for t_idx, d_idx in zip(track_indices, det_indices):
            if cost_matrix[t_idx, d_idx] < np.inf:
                associations.append(
                    (tracks[t_idx], detections[d_idx], cost_matrix[t_idx, d_idx])
                )
        
        # Add unassociated tracks and detections
        # ... implementation
        
        return associations