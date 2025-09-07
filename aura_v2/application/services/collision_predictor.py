# aura_v2/application/services/collision_predictor.py
import numpy as np
from typing import List
from ...domain.entities.track import Track
from ...domain.services.colission_prediction import CollisionPredictor
from ...domain.value_objects.collision import Collision

class BasicCollisionPredictor(CollisionPredictor):
    """Basic collision prediction implementation"""
    
    def __init__(self, collision_threshold: float = 10.0, time_horizon: float = 30.0):
        self.collision_threshold = collision_threshold  # meters
        self.time_horizon = time_horizon  # seconds
    
    def predict(self, tracks: List[Track]) -> List[Collision]:
        """Predicts potential collisions between tracks."""
        collisions = []
        
        for i, track1 in enumerate(tracks):
            for j, track2 in enumerate(tracks[i+1:], i+1):
                collision = self._check_collision_pair(track1, track2)
                if collision:
                    collisions.append(collision)
        
        return collisions
    
    def _check_collision_pair(self, track1: Track, track2: Track) -> Collision:
        """Check if two tracks are on collision course."""
        # Current positions
        p1 = np.array([track1.state.position.x, track1.state.position.y, track1.state.position.z])
        p2 = np.array([track2.state.position.x, track2.state.position.y, track2.state.position.z])
        
        # Velocities
        v1 = np.array([track1.state.velocity.vx, track1.state.velocity.vy, track1.state.velocity.vz])
        v2 = np.array([track2.state.velocity.vx, track2.state.velocity.vy, track2.state.velocity.vz])
        
        # Relative position and velocity
        rel_pos = p2 - p1
        rel_vel = v2 - v1
        
        # If relative velocity is zero, no collision
        rel_speed = np.linalg.norm(rel_vel)
        if rel_speed < 0.01:  # practically stationary
            return None
        
        # Time to closest approach
        t_closest = -np.dot(rel_pos, rel_vel) / (rel_speed ** 2)
        
        # Only consider future collisions within time horizon
        if t_closest < 0 or t_closest > self.time_horizon:
            return None
        
        # Distance at closest approach
        closest_distance = np.linalg.norm(rel_pos + rel_vel * t_closest)
        
        # Check if collision will occur
        if closest_distance < self.collision_threshold:
            probability = 1.0 - (closest_distance / self.collision_threshold)
            return Collision(
                track1=track1,
                track2=track2,
                time_to_collision=t_closest,
                probability=probability
            )
        
        return None