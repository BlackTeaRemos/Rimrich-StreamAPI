

from typing import List, Optional

from src.game_events.templates.game_event_template_definition import GameEventTemplateDefinition
from src.game_events.templates.game_event_template_entry import GameEventTemplateEntry
from src.game_events.templates.game_event_template_repository import GameEventTemplateRepository


class GameEventTemplateCatalogService:
    def __init__(self, repository: GameEventTemplateRepository) -> None:
        self._repository = repository
        self._entries: List[GameEventTemplateEntry] = []
        self.Reload()

    def Reload(self) -> None:
        self._entries = self._repository.LoadAll()

    def GetEntries(self) -> List[GameEventTemplateEntry]:
        return list(self._entries)

    def GetAll(self) -> List[GameEventTemplateDefinition]:
        return [entry.definition for entry in self._entries]

    def GetByTags(self, tags: List[str]) -> List[GameEventTemplateDefinition]:
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

    def PickRandom(self, tags: Optional[List[str]] = None) -> Optional[GameEventTemplateDefinition]:
        pool = self.GetByTags(tags or [])
        if not pool:
            return None
        return pool[0]
