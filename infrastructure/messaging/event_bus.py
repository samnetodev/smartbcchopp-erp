from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from core.shared.domain_event import DomainEvent

EventHandler = Callable[[DomainEvent], Awaitable[None]]


@dataclass
class EventBus:
    _handlers: dict[str, list[EventHandler]] = field(default_factory=dict)

    def register(self, event_type: str, handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        event_type = type(event).__name__
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            await handler(event)
