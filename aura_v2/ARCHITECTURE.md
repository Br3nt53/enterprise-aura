# AURA Clean Architecture

## Layers
1. **Domain**: Pure business logic, no dependencies
2. **Application**: Use cases and orchestration
3. **Infrastructure**: External interfaces (ROS2, files, network)

## Dependency Rule
Dependencies only point inward: Infrastructure → Application → Domain
