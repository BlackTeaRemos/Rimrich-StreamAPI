from src.core.events.event import Event


class CloseOverlayEvent(Event):
    """
    CloseOverlayEvent indicates overlay shutdown

    Args:
        None: no arguments example None

    Returns:
        CloseOverlayEvent: initialized event instance example CloseOverlayEvent()
    """

    def __init__(self) -> None:
        super().__init__("close_overlay")
