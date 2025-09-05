# aura_v2/tests/integration/test_pipeline_e2e.py
import pytest
import asyncio
from aura_v2.infrastructure.config.container import Container

@pytest.fixture
async def test_container():
    """Create test container with mocked external dependencies"""
    container = Container()
    container.config.from_dict({
        'tracking': {
            'association_method': 'hungarian',
            'gate_threshold': 2.0,
        },
        'database': {
            'connection_string': 'sqlite:///:memory:'
        }
    })
    container.wire(modules=['aura_v2.application', 'aura_v2.infrastructure'])
    yield container
    await container.shutdown_resources()

@pytest.mark.asyncio
async def test_full_tracking_pipeline(test_container):
    """Test complete tracking pipeline end-to-end"""
    # Arrange
    pipeline = test_container.tracking_pipeline()
    test_detections = create_test_detection_sequence()
    
    # Act
    results = []
    async for result in pipeline.process(test_detections):
        results.append(result)
    
    # Assert
    assert len(results) > 0
    assert all(r.active_tracks for r in results)
    assert results[-1].metrics.mota > 0.9