from src.core.events.event import Event


class AppExitEvent(Event):
    def __init__(self) -> None:
        super().__init__("app_exit")
