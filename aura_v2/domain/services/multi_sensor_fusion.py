# aura_v2/domain/services/multi_sensor_fusion.py
from typing import List, Dict, Tuple
import numpy as np
from dataclasses import dataclass
from filterpy.kalman import UnscentedKalmanFilter

from ..entities import Track, Detection
from ..ports import FusionStrategy

@dataclass
class SensorCharacteristics:
    """Defines sensor capabilities and uncertainties"""
    sensor_id: str
    accuracy: float  # meters
    update_rate: float  # Hz
    detection_probability: float
    false_alarm_rate: float
    covariance: np.ndarray

class MultiSensorFusion(FusionStrategy):
    """
    Advanced multi-sensor fusion using Unscented Kalman Filter
    Handles radar, lidar, camera with different characteristics
    """
    
    def __init__(self, sensor_configs: Dict[str, SensorCharacteristics]):
        self.sensor_configs = sensor_configs
        self.ukf = self._initialize_ukf()
    
    def _initialize_ukf(self) -> UnscentedKalmanFilter:
        """Initialize UKF for 6-DOF tracking"""
        def fx(x, dt):
            """State transition function"""
            F = np.eye(6)
            F[0:3, 3:6] = np.eye(3) * dt
            return F @ x
        
        def hx(x):
            """Measurement function"""
            return x[0:3]  # Position only
        
        points = filterpy.kalman.MerweScaledSigmaPoints(
            n=6, alpha=0.001, beta=2, kappa=-3
        )
        
        ukf = UnscentedKalmanFilter(
            dim_x=6, dim_z=3, 
            dt=0.1, 
            fx=fx, hx=hx,
            points=points
        )
        
        # Process noise
        ukf.Q = np.eye(6) * 0.1
        
        return ukf
    
    def fuse(self, 
             track: Track,
             detections: List[Detection]) -> Tuple[Track, float]:
        """
        Fuse multi-sensor detections into unified track state
        
        Returns updated track and fusion confidence
        """
        if not detections:
            # Predict only
            track.state = track.state.predict(0.1)
            return track, track.confidence.value * 0.95
        
        # Group detections by sensor
        sensor_groups = {}
        for det in detections:
            sensor_groups.setdefault(det.sensor_id, []).append(det)
        
        # Initialize state
        x = np.hstack([
            track.state.position.to_array(),
            track.state.velocity.to_array()
        ])
        
        # Fuse each sensor's measurements
        fusion_confidence = 1.0
        
        for sensor_id, sensor_dets in sensor_groups.items():
            sensor_config = self.sensor_configs[sensor_id]
            
            # Weight by sensor accuracy
            weight = 1.0 / sensor_config.accuracy
            
            for det in sensor_dets:
                # Measurement
                z = det.position.to_array()
                
                # Measurement noise (sensor-specific)
                self.ukf.R = sensor_config.covariance
                
                # Update
                self.ukf.update(z)
                
                # Track confidence from this sensor
                fusion_confidence *= (
                    sensor_config.detection_probability * 
                    (1 - sensor_config.false_alarm_rate) *
                    det.confidence.value
                )
        
        # Extract updated state
        track.state.position = Position3D.from_array(self.ukf.x[0:3])
        track.state.velocity = Velocity3D.from_array(self.ukf.x[3:6])
        track.state.covariance = Covariance(self.ukf.P)
        
        # Update track confidence
        track.confidence = Confidence(min(0.99, fusion_confidence))
        
        return track, fusion_confidence