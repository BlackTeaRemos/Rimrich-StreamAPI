from typing import Dict, List, Tuple

from src.events.close_overlay_event import CloseOverlayEvent
from src.core.events.event_bus import EventBus
from src.events.show_overlay_event import ShowOverlayEvent
from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.game_events.game_event_definition import GameEventDefinition


class VotingService:
    def __init__(self, catalogService: GameEventCatalogService, eventBus: EventBus) -> None:
        self.catalogService = catalogService
        self.eventBus = eventBus
        self._activeDefinitions: List[GameEventDefinition] = []
        self._activeOptions: List[str] = []
        self._counts: List[int] = []
        self._userVotes: Dict[str, int] = {}
        self._recentVoters: List[str] = []

    def ReloadDefinitions(self) -> None:
        try:
            self.catalogService.Reload()
        except Exception:
            pass

    def __ResolveOptionText(self, definition: GameEventDefinition) -> str:
        try:
            userMessage = definition.userMessage
            if userMessage is not None:
                text = str(userMessage).strip()
                if text != "":
                    return text
        except Exception:
            pass

        return definition.label

    def StartPoll(self) -> None:
        definitions = [definition for definition in self.catalogService.GetAll() if not bool(getattr(definition, "hidden", False))][:4]
        self.StartPollWithDefinitions(definitions)

    def StartPollWithDefinitions(self, definitions: List[GameEventDefinition]) -> None:
        if not definitions:
            self._activeDefinitions = []
            self._activeOptions = ["Option 1", "Option 2", "Option 3", "Option 4"]
        else:
            self._activeDefinitions = list(definitions)[:4]
            self._activeOptions = [self.__ResolveOptionText(definition) for definition in self._activeDefinitions]

        self._counts = [0 for _ in self._activeOptions]
        self._userVotes = {}
        self._recentVoters = []
        self.__Publish()

    def StopPoll(self) -> None:
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
        pairs: List[Tuple[str, int]] = list(zip(self._activeOptions, self._counts))
        try:
            self.eventBus.Publish(ShowOverlayEvent(pairs, self._recentVoters))
        except Exception:
            pass

    def __RecalculateCounts(self) -> None:
        self._counts = [0 for _ in self._activeOptions]
        for index in self._userVotes.values():
            if 0 <= index < len(self._counts):
                self._counts[index] = self._counts[index] + 1

    def __TrackRecent(self, user: str) -> None:
        try:
            self._recentVoters = [name for name in self._recentVoters if name != user]
            self._recentVoters.append(user)
            self._recentVoters = self._recentVoters[-3:]
        except Exception:
            pass
