from dependency_injector import containers, providers
from aura_v2.application.pipelines.tracking_pipeline import TrackingPipeline

class Container(containers.DeclarativeContainer):
    """
    DI container for the tracking application.
    See https://python-dependency-injector.ets-labs.org/
    """
    config = providers.Configuration()

    tracking_pipeline = providers.Factory(
        TrackingPipeline,
    )
