# aura_v2/tests/integration/test_multi_sensor_tracking.py
import pytest
import asyncio
import numpy as np
from datetime import datetime, timedelta

from aura_v2.domain.entities import Detection, Position3D, Confidence
from aura_v2.infrastructure.config.container import Container

@pytest.fixture
async def container():
    """Create test container with mocked sensors"""
    container = Container()
    container.config.from_dict({
        'tracking': {'algorithm': 'bytetrack', 'use_gpu': False},
        'database': {'connection_string': 'mongodb://localhost:27017/test'},
        'messaging': {'kafka_url': 'localhost:9092'}
    })
    yield container
    await container.shutdown()

@pytest.mark.asyncio
async def test_multi_target_crossing_scenario(container):
    """
    Test the most challenging scenario:
    Multiple targets crossing paths with sensor disagreement
    """
    
    # Setup
    pipeline = container.tracking_pipeline()
    
    # Create synthetic scenario
    # Target 1: Moving left to right
    # Target 2: Moving right to left  
    # They cross at t=5 seconds
    
    detections_timeline = []
    
    for t in range(100):  # 10 seconds at 10Hz
        timestamp = datetime.now() + timedelta(seconds=t/10)
        
        # Target 1 position
        t1_x = -50 + t * 1.0  # 1 m/s
        t1_y = 0
        
        # Target 2 position
        t2_x = 50 - t * 1.0
        t2_y = 0
        
        # Radar detections (good range, poor lateral)
        radar = [
            Detection(
                timestamp=timestamp,
                position=Position3D(t1_x + np.random.normal(0, 1), 
                                  t1_y + np.random.normal(0, 5), 0),
                confidence=Confidence(0.9),
                sensor_id='radar'
            ),
            Detection(
                timestamp=timestamp,
                position=Position3D(t2_x + np.random.normal(0, 1),
                                  t2_y + np.random.normal(0, 5), 0),
                confidence=Confidence(0.9),
                sensor_id='radar'
            )
        ]
        
        # Camera detections (good lateral, poor range)
        camera = [
            Detection(
                timestamp=timestamp,
                position=Position3D(t1_x + np.random.normal(0, 5),
                                  t1_y + np.random.normal(0, 0.5), 0),
                confidence=Confidence(0.7),
                sensor_id='camera'
            ),
            Detection(
                timestamp=timestamp,
                position=Position3D(t2_x + np.random.normal(0, 5),
                                  t2_y + np.random.normal(0, 0.5), 0),
                confidence=Confidence(0.7),
                sensor_id='camera'
            )
        ]
        
        # Lidar detections (very accurate but may miss)
        lidar = []
        if np.random.random() > 0.1:  # 90% detection rate
            lidar.append(Detection(
                timestamp=timestamp,
                position=Position3D(t1_x + np.random.normal(0, 0.1),
                                  t1_y + np.random.normal(0, 0.1), 0),
                confidence=Confidence(0.95),
                sensor_id='lidar'
            ))
        if np.random.random() > 0.1:
            lidar.append(Detection(
                timestamp=timestamp,
                position=Position3D(t2_x + np.random.normal(0, 0.1),
                                  t2_y + np.random.normal(0, 0.1), 0),
                confidence=Confidence(0.95),
                sensor_id='lidar'
            ))
        
        detections_timeline.append({
            'timestamp': timestamp,
            'radar': radar,
            'camera': camera,
            'lidar': lidar
        })
    
    # Process all detections
    results = []
    for frame in detections_timeline:
        result = await pipeline.detect_and_track.execute(
            DetectAndTrackCommand(
                radar_data=frame['radar'],
                lidar_data=frame['lidar'],
                camera_data=frame['camera'],
                timestamp=frame['timestamp']
            )
        )
        results.append(result)
    
    # Assertions
    
    # Should maintain 2 tracks throughout
    assert all(len(r.active_tracks) == 2 for r in results[10:90])
    
    # No ID switches at crossing point (frames 45-55)
    tracks_before = results[40].active_tracks
    tracks_after = results[60].active_tracks
    
    # Track IDs should be consistent
    ids_before = {t.id for t in tracks_before}
    ids_after = {t.id for t in tracks_after}
    assert ids_before == ids_after, "ID switch detected at crossing!"
    
    # Fusion should improve accuracy
    for result in results[10:90]:
        for track in result.active_tracks:
            # Fused position should be more accurate than any single sensor
            assert track.state.covariance is not None
            position_uncertainty = np.trace(track.state.covariance.matrix[:3, :3])
            assert position_uncertainty < 1.0  # Better than worst sensor
    
    # Collision should be predicted
    collision_warnings = [
        e for r in results[40:60] 
        for e in r.events 
        if isinstance(e, CollisionWarning)
    ]
    assert len(collision_warnings) > 0, "Failed to predict collision"
    
    # Performance metrics
    latencies = [r.processing_time_ms for r in results]
    assert max(latencies) < 50, f"Latency too high: {max(latencies)}ms"
    assert np.mean(latencies) < 20, f"Average latency too high: {np.mean(latencies)}ms"