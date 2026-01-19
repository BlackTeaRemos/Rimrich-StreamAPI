from typing import Callable, List, Optional

from src.events.app_started_event import AppStartedEvent
from src.core.events.event_bus import EventBus
from src.listeners.window_event_listener import WindowEventListener


class Application:
    def __init__(self, eventBus: EventBus, listeners: List[WindowEventListener], bootstrap: Optional[Callable[[], None]] = None) -> None:
        self.eventBus = eventBus
        self.listeners = listeners
        self.bootstrap = bootstrap

    def Run(self) -> None:
        try:
            for listener in self.listeners:
                listener.Register()
            if self.bootstrap is not None:
                self.bootstrap()
            self.eventBus.Publish(AppStartedEvent())
        except Exception as error:
            raise RuntimeError("Application failed to start") from error
