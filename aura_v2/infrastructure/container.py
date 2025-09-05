# infrastructure/container.py
class DIContainer:
    def __init__(self, config: Config):
        self.config = config
        self._factories = {}
        self._singletons = {}
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]):
        self._factories[interface] = factory
    
    def resolve(self, interface: Type[T]) -> T:
        if interface in self._singletons:
            return self._singletons[interface]
        return self._factories[interface]()

# infrastructure/config/container_config.py
def configure_container(config_path: Path) -> DIContainer:
    config = load_config(config_path)
    container = DIContainer(config)
    
    # Register all dependencies
    container.register_factory(
        TrackerInterface,
        lambda: create_tracker(config.tracking)
    )
    container.register_factory(
        MetricsCalculator,
        lambda: MOTMetrics(config.evaluation)
    )
    container.register_singleton(
        EventBus,
        lambda: AsyncEventBus(config.messaging)
    )
    
    return container

# application/ros_nodes/fusion_tracker_node.py
class FusionTrackerNode(Node):
    def __init__(self, tracker: TrackerInterface, event_bus: EventBus):
        super().__init__('fusion_tracker')
        self.tracker = tracker  # ✅ Injected
        self.event_bus = event_bus  # ✅ Injected