from typing import Dict, List, Tuple

from src.events.close_overlay_event import CloseOverlayEvent
from src.core.events.event_bus import EventBus
from src.events.show_overlay_event import ShowOverlayEvent
from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.game_events.game_event_definition import GameEventDefinition


class RimApiService:
    """Manage Rim API events and provide poll functionality driven from Rim events.

    Args:
        catalogService (GameEventCatalogService): service providing available events.
        eventBus (EventBus): shared event bus.
    """

    def __init__(self, catalogService: GameEventCatalogService, eventBus: EventBus) -> None:
        self.catalogService = catalogService  # static event definitions
        self.eventBus = eventBus  # bus
        self._activeDefinitions: List[GameEventDefinition] = []  # active poll definitions
        self._activeOptions: List[str] = []  # poll options
        self._counts: List[int] = []  # poll counts
        self._userVotes: Dict[str, int] = {}  # user vote index map
        self._recentVoters: List[str] = []  # recent voter order

    def GetAvailableEventLabels(self) -> List[str]:
        """GetAvailableEventLabels returns loaded event labels for display."""

        try:
            return [definition.label for definition in self.catalogService.GetAll()]
        except Exception:
            return []

    def ReloadDefinitions(self) -> None:
        """ReloadDefinitions reloads JSONC event definitions from disk."""

        try:
            self.catalogService.Reload()
        except Exception:
            pass

    def StartPoll(self) -> None:
        """Start a poll using the first four available event definitions.

        Returns:
            None
        """

        definitions = self.catalogService.GetAll()[:4]
        if not definitions:
            self.StartPollWithDefinitions([])
            return
        self.StartPollWithDefinitions(definitions)

    def StartPollWithDefinitions(self, definitions: List[GameEventDefinition]) -> None:
        """StartPollWithDefinitions starts a poll with the provided definitions."""

        if not definitions:
            self._activeDefinitions = []
            self._activeOptions = ["Option 1", "Option 2", "Option 3", "Option 4"]
        else:
            self._activeDefinitions = list(definitions)[:4]
            self._activeOptions = [definition.label for definition in self._activeDefinitions]
        self._counts = [0 for _ in self._activeOptions]
        self._userVotes = {}
        self._recentVoters = []
        self.__Publish()

    def StopPoll(self) -> None:
        """Stop the current poll, clear internal state, and close the overlay.

        Returns:
            None
        """

        self._activeOptions = []
        self._activeDefinitions = []
        self._counts = []
        self._userVotes = {}
        self._recentVoters = []
        try:
            self.eventBus.Publish(CloseOverlayEvent())
        except Exception:
            pass

    def HandleChat(self, user: str, content: str) -> None:
        """Process chat input as a poll vote.

        Args:
            user (str): author name, e.g. "viewer".
            content (str): chat text with vote choice, e.g. "1".

        Returns:
            None
        """

        if not self._activeOptions:
            return
        if user is None or user.strip() == "":
            return
        choice = content.strip()
        if choice not in ["1", "2", "3", "4"]:
            return
        index = int(choice) - 1
        if index >= len(self._counts):
            return
        self._userVotes[user] = index
        self.__TrackRecent(user)
        self.__RecalculateCounts()
        self.__Publish()

    def GetWinnerIndex(self) -> int:
        if not self._counts:
            return -1
        maxVotes = max(self._counts)
        if maxVotes <= 0:
            return -1
        return self._counts.index(maxVotes)

    def GetActiveDefinitions(self) -> List[GameEventDefinition]:
        return list(self._activeDefinitions)

    def GetCounts(self) -> List[int]:
        return list(self._counts)

    def __Publish(self) -> None:
        """Publish the current poll state to the overlay via event bus.

        Returns:
            None
        """

        pairs: List[Tuple[str, int]] = list(zip(self._activeOptions, self._counts))
        try:
            self.eventBus.Publish(ShowOverlayEvent(pairs, self._recentVoters))
        except Exception:
            pass

    def __RecalculateCounts(self) -> None:
        """Recalculate poll counts based on recorded user votes.

        Returns:
            None
        """

        self._counts = [0 for _ in self._activeOptions]
        for index in self._userVotes.values():
            if 0 <= index < len(self._counts):
                self._counts[index] = self._counts[index] + 1

    def __TrackRecent(self, user: str) -> None:
        """Update the recent voters list, keeping the most recent entries.

        Args:
            user (str): username.

        Returns:
            None
        """

        try:
            self._recentVoters = [name for name in self._recentVoters if name != user]
            self._recentVoters.append(user)
            self._recentVoters = self._recentVoters[-3:]
        except Exception:
            pass
