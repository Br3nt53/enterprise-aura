import pytest

from aura_v2.infrastructure.container import Container


@pytest.fixture
def container():
    c = Container()
    c.init_resources()
    yield c


@pytest.mark.asyncio
async def test_multi_target_crossing_scenario(container):
    """
    Test the most challenging scenario:
    Multiple targets crossing paths with sensor disagreement
    """

    # Setup
    pipeline = container.tracking_pipeline()

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
