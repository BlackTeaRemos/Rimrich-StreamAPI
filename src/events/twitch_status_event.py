from src.core.events.event import Event


class TwitchStatusEvent(Event):
    def __init__(self, status: str, message: str = "") -> None:
        super().__init__("twitch_status")
        self.status = str(status or "")
        self.message = str(message or "")
