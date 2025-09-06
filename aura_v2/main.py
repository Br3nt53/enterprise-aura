# aura_v2/main.py - Fixed version with proper architecture integration
"""
AURA Enterprise v2 - Main application with proper architectural wiring
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import actual domain and infrastructure components
from aura_v2.infrastructure.tracking.modern_tracker import ModernTracker, TrackingResult
from aura_v2.domain.entities import Detection, Position3D, Confidence
from aura_v2.domain.services.multi_sensor_fusion import MultiSensorFusion, SensorCharacteristics
import numpy as np


class DetectionInput(BaseModel):
    """API input for detection"""
    timestamp: datetime
    position: Dict[str, float]  # {x, y, z}
    confidence: float = Field(ge=0.0, le=1.0)
    sensor_id: str
    attributes: Optional[Dict[str, Any]] = None


class TrackOutput(BaseModel):
    """API output for track"""
    id: str
    position: Dict[str, float]
    velocity: Dict[str, float]
    confidence: float
    status: str
    threat_level: str
    created_at: datetime
    updated_at: datetime


class TrackRequest(BaseModel):
    """API request for tracking"""
    radar_detections: List[DetectionInput] = Field(default_factory=list)
    camera_detections: List[DetectionInput] = Field(default_factory=list)
    lidar_detections: List[DetectionInput] = Field(default_factory=list)
    timestamp: Optional[datetime] = None


class TrackResponse(BaseModel):
    """API response for tracking"""
    active_tracks: List[TrackOutput]
    new_tracks: List[TrackOutput] = Field(default_factory=list)
    deleted_tracks: List[str] = Field(default_factory=list)
    threats: List[Dict[str, Any]] = Field(default_factory=list)
    processing_time_ms: float = 0.0
    frame_id: int = 0


class AURAApplication:
    """
    Main AURA application with proper architecture integration
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = Path(config_path) if config_path else None
        self.config: Dict[str, Any] = {}
        self.app: Optional[FastAPI] = None
        
        # Core components
        self.tracker: Optional[ModernTracker] = None
        self.fusion_service: Optional[MultiSensorFusion] = None
        self._frame_id: int = 0
        
    async def initialize(self) -> None:
        """Initialize application components"""
        
        # Load configuration
        if self.config_path and self.config_path.exists():
            self._load_config()
        
        # Initialize tracker
        self.tracker = ModernTracker(
            max_age=self.config.get('tracking', {}).get('max_age', 30),
            min_hits=self.config.get('tracking', {}).get('min_hits', 3),
            max_distance=self.config.get('tracking', {}).get('max_distance', 50.0)
        )
        
        # Initialize sensor fusion service
        sensor_configs = {
            'radar': SensorCharacteristics(
                sensor_id='radar',
                accuracy=2.0,  # meters
                update_rate=20.0,  # Hz
                detection_probability=0.95,
                false_alarm_rate=0.01,
                covariance=np.eye(3) * 4.0  # 2m std dev
            ),
            'camera': SensorCharacteristics(
                sensor_id='camera',
                accuracy=5.0,  # meters (range accuracy poor)
                update_rate=30.0,
                detection_probability=0.90,
                false_alarm_rate=0.05,
                covariance=np.diag([25.0, 1.0, 25.0])  # Good lateral, poor range
            ),
            'lidar': SensorCharacteristics(
                sensor_id='lidar',
                accuracy=0.2,  # meters (very accurate)
                update_rate=10.0,
                detection_probability=0.85,
                false_alarm_rate=0.001,
                covariance=np.eye(3) * 0.04  # 0.2m std dev
            )
        }
        self.fusion_service = MultiSensorFusion(sensor_configs)
        
        # Build FastAPI app
        self._build_app()
    
    def _load_config(self) -> None:
        """Load configuration from file"""
        try:
            if self.config_path.suffix in ['.yaml', '.yml']:
                import yaml
                self.config = yaml.safe_load(self.config_path.read_text()) or {}
            else:
                self.config = json.loads(self.config_path.read_text())
        except Exception as e:
            print(f"Failed to load config: {e}")
            self.config = {}
    
    def _build_app(self) -> None:
        """Build FastAPI application with endpoints"""
        
        self.app = FastAPI(
            title="AURA Enterprise v2 API",
            version="2.0.0",
            description="Real-time multi-sensor object tracking system"
        )
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "time": datetime.utcnow().isoformat(),
                "tracker_status": "active" if self.tracker else "not_initialized",
                "active_tracks": len(self.tracker.tracks) if self.tracker else 0
            }
        
        @self.app.post("/api/v1/track", response_model=TrackResponse)
        async def process_track(request: TrackRequest):
            """Main tracking endpoint with proper fusion and tracking"""
            
            if not self.tracker:
                raise HTTPException(status_code=500, detail="Tracker not initialized")
            
            self._frame_id += 1
            timestamp = request.timestamp or datetime.utcnow()
            
            # Convert API detections to domain entities
            all_detections = []
            
            for det_input in request.radar_detections:
                all_detections.append(self._to_domain_detection(det_input, 'radar'))
            
            for det_input in request.camera_detections:
                all_detections.append(self._to_domain_detection(det_input, 'camera'))
            
            for det_input in request.lidar_detections:
                all_detections.append(self._to_domain_detection(det_input, 'lidar'))
            
            # Perform multi-sensor fusion if multiple sensors have detections
            if len(all_detections) > 1:
                fused_detections = await self._fuse_detections(all_detections)
            else:
                fused_detections = all_detections
            
            # Update tracker
            result = await self.tracker.update(fused_detections, timestamp)
            
            # Convert to API response
            return self._build_response(result)
        
        @self.app.get("/api/v1/tracks")
        async def list_tracks(
            limit: int = 100,
            page: int = 1,
            threat_level: Optional[str] = None,
            status: Optional[str] = None
        ):
            """List all active tracks with filtering"""
            
            if not self.tracker:
                return {"tracks": [], "total": 0, "page": page, "limit": limit}
            
            tracks = list(self.tracker.tracks.values())
            
            # Apply filters
            if threat_level:
                tracks = [t for t in tracks if t.threat_level.name.lower() == threat_level.lower()]
            if status:
                tracks = [t for t in tracks if t.status.value == status]
            
            # Pagination
            start = (page - 1) * limit
            end = start + limit
            paginated = tracks[start:end]
            
            # Convert to output format
            track_outputs = [self._track_to_output(t) for t in paginated]
            
            return {
                "tracks": track_outputs,
                "total": len(tracks),
                "page": page,
                "limit": limit
            }
    
    def _to_domain_detection(self, det_input: DetectionInput, sensor_type: str) -> Detection:
        """Convert API detection to domain entity"""
        return Detection(
            timestamp=det_input.timestamp,
            position=Position3D(
                x=det_input.position['x'],
                y=det_input.position['y'],
                z=det_input.position.get('z', 0.0)
            ),
            confidence=Confidence(det_input.confidence),
            sensor_id=det_input.sensor_id or sensor_type,
            attributes=det_input.attributes or {}
        )
    
    async def _fuse_detections(self, detections: List[Detection]) -> List[Detection]:
        """Fuse multiple detections using clustering and weighted averaging"""
        
        # Simple clustering based on distance
        clusters = []
        threshold = 5.0  # 5 meter clustering threshold
        
        for det in detections:
            assigned = False
            for cluster in clusters:
                # Check if detection belongs to existing cluster
                center = cluster[0]
                dist = det.position.distance_to(center.position)
                if dist < threshold:
                    cluster.append(det)
                    assigned = True
                    break
            
            if not assigned:
                clusters.append([det])
        
        # Fuse each cluster
        fused_detections = []
        for cluster in clusters:
            if len(cluster) == 1:
                fused_detections.append(cluster[0])
            else:
                # Weighted average based on sensor accuracy
                weights = []
                positions = []
                
                for det in cluster:
                    # Get sensor weight (inverse of accuracy)
                    sensor_type = det.sensor_id.split('_')[0]  # Extract base sensor type
                    if sensor_type in ['radar', 'camera', 'lidar']:
                        accuracy = self.fusion_service.sensor_configs[sensor_type].accuracy
                        weight = 1.0 / accuracy
                    else:
                        weight = 1.0
                    
                    weights.append(weight * det.confidence.value)
                    positions.append([det.position.x, det.position.y, det.position.z])
                
                # Normalize weights
                weights = np.array(weights)
                weights = weights / weights.sum()
                
                # Weighted average position
                positions = np.array(positions)
                fused_pos = np.average(positions, weights=weights, axis=0)
                
                # Combined confidence
                combined_confidence = min(0.99, np.mean([d.confidence.value for d in cluster]) * 1.1)
                
                fused_detections.append(Detection(
                    timestamp=cluster[0].timestamp,
                    position=Position3D(x=fused_pos[0], y=fused_pos[1], z=fused_pos[2]),
                    confidence=Confidence(combined_confidence),
                    sensor_id='fused',
                    attributes={'source_sensors': [d.sensor_id for d in cluster]}
                ))
        
        return fused_detections
    
    def _track_to_output(self, track) -> TrackOutput:
        """Convert domain track to API output"""
        return TrackOutput(
            id=str(track.id),
            position={
                'x': track.state.position.x,
                'y': track.state.position.y,
                'z': track.state.position.z
            },
            velocity={
                'vx': track.state.velocity.vx,
                'vy': track.state.velocity.vy,
                'vz': track.state.velocity.vz
            },
            confidence=track.confidence.value,
            status=track.status.value,
            threat_level=track.threat_level.name.lower(),
            created_at=track.created_at,
            updated_at=track.updated_at
        )
    
    def _build_response(self, result: TrackingResult) -> TrackResponse:
        """Build API response from tracking result"""
        
        # Identify threats
        threats = []
        for track in result.active_tracks:
            if track.threat_level.value >= 3:  # HIGH or CRITICAL
                threats.append({
                    'track_id': str(track.id),
                    'threat_level': track.threat_level.name,
                    'position': {
                        'x': track.state.position.x,
                        'y': track.state.position.y,
                        'z': track.state.position.z
                    },
                    'velocity_magnitude': (
                        track.state.velocity.vx**2 + 
                        track.state.velocity.vy**2 + 
                        track.state.velocity.vz**2
                    )**0.5
                })
        
        return TrackResponse(
            active_tracks=[self._track_to_output(t) for t in result.active_tracks],
            new_tracks=[self._track_to_output(t) for t in result.new_tracks],
            deleted_tracks=[str(t.id) for t in result.deleted_tracks],
            threats=threats,
            processing_time_ms=result.processing_time_ms,
            frame_id=self._frame_id
        )
    
    async def shutdown(self) -> None:
        """Cleanup on shutdown"""
        # Add any cleanup logic here
        pass


# CLI remains the same
app_cli = typer.Typer(add_completion=False, help="AURA Enterprise v2 CLI")

@app_cli.command("run")
def run(
    host: str = typer.Option("0.0.0.0", help="Bind host"),
    port: int = typer.Option(8000, help="Port"),
    config: Optional[str] = typer.Option(None, help="Path to config file"),
    reload: bool = typer.Option(False, help="Enable auto-reload")
):
    """Run AURA tracking server"""
    app = AURAApplication(Path(config) if config else None)
    asyncio.run(app.initialize())
    uvicorn.run(app.app, host=host, port=port, reload=reload)

if __name__ == "__main__":
    app_cli()