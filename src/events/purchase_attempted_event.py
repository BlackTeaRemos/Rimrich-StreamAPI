from src.core.events.event import Event


class PurchaseAttemptedEvent(Event):
    """Event fired when a user attempts to purchase a game event."""

    def __init__(self, username: str, eventIdentifier: str, success: bool, message: str) -> None:
        super().__init__("purchase_attempted")
        self.username = username
        self.eventIdentifier = eventIdentifier
        self.success = success
        self.message = message
