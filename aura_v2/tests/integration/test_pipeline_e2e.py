import pytest
from aura_v2.infrastructure.container import Container

@pytest.fixture
async def test_container():
    c = Container()
    await c.init_resources()
    yield c
    await c.shutdown_resources()

@pytest.mark.asyncio
async def test_full_tracking_pipeline(test_container):
    """Test complete tracking pipeline end-to-end"""
    # Arrange
    pipeline = await test_container.tracking_pipeline()
    sensor_data = [
        {"sensor_id": "radar_1", "x": 10, "y": 20, "timestamp": 1.0},
        {"sensor_id": "camera_1", "x": 10.1, "y": 20.2, "timestamp": 1.1},
        {"sensor_id": "lidar_1", "x": 9.9, "y": 19.8, "timestamp": 1.2},
    ]

    # Act
    tracks = await pipeline.process(sensor_data)

    # Assert
    assert len(tracks) == 1
    track = tracks[0]
    assert track.id is not None
    # Check that the fused position is a reasonable average
    assert 9.9 < track.predicted_position.x < 10.1
    assert 19.8 < track.predicted_position.y < 20.2
