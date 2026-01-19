from typing import List, Tuple

from src.core.events.event import Event


class ShowOverlayEvent(Event):
    """
    ShowOverlayEvent carries up to ten vote entries to render on the overlay

    Args:
        votes (list[tuple[str, int]]): collection of name and vote count pairs example [("Option A", 3)]
        voters (list[str]): recent voters example ["user1", "user2"]

    Returns:
        ShowOverlayEvent: initialized event instance example ShowOverlayEvent([("Option A", 3)])
    """

    def __init__(self, votes: List[Tuple[str, int]], voters: List[str] | None = None) -> None:
        trimmed = votes[:10]
        super().__init__("show_overlay")
        self.votes = trimmed  # top votes to display
        safeVoters = voters if voters is not None else []
        self.voters = safeVoters[:3]
