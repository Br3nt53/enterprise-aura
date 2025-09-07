import pytest
from aura_v2.infrastructure.container import Container

@pytest.fixture
async def container():
    c = Container()
    await c.init_resources()
    yield c
    await c.shutdown_resources()

@pytest.mark.asyncio
async def test_multi_target_crossing_scenario(container):
    """
    Test the most challenging scenario:
    Multiple targets crossing paths with sensor disagreement
    """

    # Setup
    pipeline = await container.tracking_pipeline()

    # Define sensor data for two targets (A and B)
    # Target A: Moves from left to right
    # Target B: Moves from right to left
    sensor_data_t1 = [
        {"sensor_id": "radar_1", "x": 10, "y": 50, "timestamp": 1.0},
        {"sensor_id": "lidar_1", "x": 90, "y": 50, "timestamp": 1.0},
    ]
    sensor_data_t2 = [
        {"sensor_id": "radar_1", "x": 20, "y": 50, "timestamp": 2.0},
        {"sensor_id": "lidar_1", "x": 80, "y": 50, "timestamp": 2.0},
    ]

    # Act
    tracks_t1 = await pipeline.process(sensor_data_t1)
    tracks_t2 = await pipeline.process(sensor_data_t2)

    # Assert
    # Check that two tracks are created and maintained
    assert len(tracks_t1) == 2
    assert len(tracks_t2) == 2
    
    # Optional: More detailed checks on track positions and IDs
    track_a_t1 = next(t for t in tracks_t1 if t.predicted_position.x < 50)
    track_b_t1 = next(t for t in tracks_t1 if t.predicted_position.x > 50)
    
    track_a_t2 = next(t for t in tracks_t2 if t.id == track_a_t1.id)
    track_b_t2 = next(t for t in tracks_t2 if t.id == track_b_t1.id)
    
    assert track_a_t2.predicted_position.x > track_a_t1.predicted_position.x
    assert track_b_t2.predicted_position.x < track_b_t1.predicted_position.x
