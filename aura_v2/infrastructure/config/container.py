# aura_v2/infrastructure/config/container.py
from dependency_injector import containers, providers
from dependency_injector.ext import aiohttp
import logging

class Container(containers.DeclarativeContainer):
    """DI Container for the entire application"""
    
    # Configuration
    config = providers.Configuration()
    
    # Logging
    logging = providers.Resource(
        logging.basicConfig,
        level=config.logging.level,
        format=config.logging.format,
    )
    
    # Domain Services
    association_strategy = providers.Selector(
        config.tracking.association_method,
        hungarian=providers.Singleton(
            HungarianAssociation,
            gate_threshold=config.tracking.gate_threshold,
        ),
        nearest=providers.Singleton(
            NearestNeighborAssociation,
            max_distance=config.tracking.max_distance,
        ),
    )
    
    # Infrastructure Adapters
    track_repository = providers.Singleton(
        PostgresTrackRepository,
        connection_string=config.database.connection_string,
    )
    
    event_bus = providers.Singleton(
        AsyncEventBus,
        broker_url=config.messaging.broker_url,
    )
    
    telemetry = providers.Singleton(
        TelemetrySystem,
        opentelemetry_endpoint=config.telemetry.endpoint,
        service_name=config.application.name,
    )
    
    # Application Services
    process_detections_use_case = providers.Factory(
        ProcessDetectionsUseCase,
        track_repository=track_repository,
        association_service=association_strategy,
        event_publisher=event_bus,
        track_manager=providers.Singleton(TrackManager),
    )
    
    # ROS2 Adapters (if ROS2 is available)
    ros2_detector = providers.Singleton(
        ROS2DetectionAdapter,
        node_name=config.ros2.node_name,
        topic=config.ros2.detection_topic,
    )
    
    # Main Pipeline
    tracking_pipeline = providers.Singleton(
        TrackingPipeline,
        detection_source=ros2_detector,
        process_detections_use_case=process_detections_use_case,
        evaluation_use_case=providers.Singleton(EvaluationUseCase),
        output_sink=providers.Singleton(
            CompositeOutputSink,
            sinks=[
                providers.Singleton(JSONLOutputSink),
                providers.Singleton(ROS2OutputSink),
            ],
        ),
    )