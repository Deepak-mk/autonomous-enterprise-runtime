from typing import Dict, List, Callable, Any
from coordination_bus.trace_logger import TraceLogger

class Event:
    def __init__(self, topic: str, sender: str, payload: Dict[str, Any]):
        self.topic = topic
        self.sender = sender
        self.payload = payload

class EventBus:
    def __init__(self, logger: TraceLogger):
        self.logger = logger
        # Map of topic -> list of callbacks (callable functions that accept an Event object)
        self.subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self.interceptor = None

    def subscribe(self, topic: str, handler: Callable[[Event], None]):
        """Subscribes an agent callback handler to a specific topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)
        self.logger.log(
            sender="EVENT_BUS",
            event_type="SUBSCRIBE",
            topic=topic,
            message=f"New subscriber registered: {handler.__self__.__class__.__name__ if hasattr(handler, '__self__') else handler.__name__}"
        )

    def publish(self, topic: str, sender: str, payload: Dict[str, Any], interceptor: Any = None):
        """Publishes an event to all subscribers, passing through a policy/arbitration interceptor if configured."""
        self.logger.log(
            sender="EVENT_BUS",
            event_type="PUBLISH",
            topic=topic,
            message=f"Event published by '{sender}'",
            payload=payload
        )
        
        event = Event(topic=topic, sender=sender, payload=payload)
        
        # If an interceptor (coordination coordinator) is registered, pass it through validation first
        active_interceptor = interceptor or self.interceptor
        if active_interceptor:
            allowed = active_interceptor.verify_and_route(event)
            if not allowed:
                return

        # Distribute event to subscribers
        handlers = self.subscribers.get(topic, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                self.logger.log(
                    sender="EVENT_BUS",
                    event_type="ERROR",
                    topic=topic,
                    message=f"Failed to dispatch event to handler: {e}"
                )
