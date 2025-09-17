# aura_v2/application/events/event_publisher.py
from typing import Any


class EventPublisher:
    """Publishes events to a message bus, log, or callback."""

    def publish(self, event: Any) -> None:
        # In a real system, this would send to a bus, log, or callback
        print(f"Event published: {event}")
