import random
from typing import List, Optional

from src.game_events.game_event_entry import GameEventEntry
from src.game_events.game_event_definition import GameEventDefinition
from src.game_events.game_event_repository import GameEventRepository


class GameEventCatalogService:
    def __init__(self, repository: GameEventRepository) -> None:
        self._repository = repository
        self._entries: List[GameEventEntry] = []
        self.Reload()

    def Reload(self) -> None:
        self._entries = self._repository.LoadAll()

    def GetEntries(self) -> List[GameEventEntry]:
        return list(self._entries)

    def GetAll(self) -> List[GameEventDefinition]:
        return [entry.definition for entry in self._entries]

    def GetByTags(self, tags: List[str]) -> List[GameEventDefinition]:
        required = {tag for tag in [str(value).strip() for value in tags] if tag}
        if not required:
            return self.GetAll()
        return [definition for definition in self.GetAll() if required.issubset(set(definition.tags))]

    def GetAllTags(self) -> List[str]:
        tags = set()
        for definition in self.GetAll():
            for tag in definition.tags:
                if str(tag).strip():
                    tags.add(str(tag))
        return sorted(tags)

    def PickRandom(self, tags: Optional[List[str]] = None) -> Optional[GameEventDefinition]:
        pool = self.GetByTags(tags or [])
        if not pool:
            return None

        weights = [max(0.0, float(definition.probability)) for definition in pool]
        if all(weight == 0.0 for weight in weights):
            return random.choice(pool)
        return random.choices(pool, weights=weights, k=1)[0]
