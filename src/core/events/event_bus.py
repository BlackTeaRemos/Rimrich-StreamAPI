from typing import Callable, Dict, List, Type

from src.core.events.event import Event


class EventBus:

    def __init__(self) -> None:
        self._subscribers: Dict[Type[Event], List[Callable[[Event], None]]] = {}

    def Subscribe(self, eventType: Type[Event], listener: Callable[[Event], None]) -> None:
        if eventType not in self._subscribers:
            self._subscribers[eventType] = []
        self._subscribers[eventType].append(listener)

    def Publish(self, event: Event) -> None:
        listeners = self._subscribers.get(type(event), [])
        for listener in list(listeners):
            try:
                listener(event)
            except Exception as error:
                try:
                    print(f"EventBus listener failed for event {event.name}: {error}")
                except Exception:
                    pass
