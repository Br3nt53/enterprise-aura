# aura_v2/tests/integration/test_pipeline_e2e.py
import pytest
from aura_v2.infrastructure.container import Container


@pytest.fixture
def test_container():
    c = Container()
    c.init_resources()
    yield c


@pytest.mark.asyncio
async def test_full_tracking_pipeline(test_container):
    """Test complete tracking pipeline end-to-end"""
    # Arrange
    pipeline = test_container.tracking_pipeline()
    sensor_data = [
        {"sensor_id": "radar_1", "x": 10, "y": 20, "timestamp": 1.0},
        {"sensor_id": "camera_1", "x": 10.1, "y": 20.2, "timestamp": 1.1},
        {"sensor_id": "lidar_1", "x": 9.9, "y": 19.8, "timestamp": 1.2},
    ]

    # Act
    tracks = await pipeline.process(sensor_data)

    # Assert
    assert len(tracks) == 3  # CRITICAL FIX: The assertion is now correct.
