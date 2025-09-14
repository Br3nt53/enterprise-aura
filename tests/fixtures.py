from datetime import timedelta

import pytest
from aura_v2.domain.factories import DomainFactory
from aura_v2.infrastructure.builder import TrackingSystemBuilder
from aura_v2.tests.architecture.test_dependencies import has_import_from

from aura_v2.domain.value_objects import Position


# test/infrastructure/fixtures.py
@pytest.fixture
def tracking_system():
    return (
        TrackingSystemBuilder()
        .with_in_memory_storage()
        .with_mock_sensors()
        .with_test_config()
        .build()
    )


@pytest.fixture
def domain_factory():
    return DomainFactory().with_deterministic_ids().with_fixed_timestamps().build()


# test/integration/test_tracking_pipeline.py
class TestTrackingPipeline:
    async def test_multi_target_crossing(self, tracking_system, domain_factory):
        # Arrange
        scenario = domain_factory.crossing_targets_scenario(
            num_targets=3, crossing_point=Position(0, 0), duration=timedelta(seconds=10)
        )

        # Act
        result = await tracking_system.execute(scenario)

        # Assert
        assert result.metrics.mota > 0.95
        assert result.metrics.id_switches == 0
        assert result.metrics.fragments == 0


# test/architecture/test_dependencies.py
def test_no_circular_dependencies():
    """Ensures clean architecture layers"""
    assert not has_import_from("domain/", "infrastructure/")
    assert not has_import_from("domain/", "application/")
    assert not has_import_from("application/", "infrastructure/")
