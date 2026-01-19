from __future__ import annotations

from typing import List, Tuple

from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.game_events.templates.game_event_template_catalog_service import GameEventTemplateCatalogService
from src.window.events.catalog_item import CatalogItem


class EventsCatalogLoader:
    def __init__(
        self,
        catalogService: GameEventCatalogService,
        templateCatalogService: GameEventTemplateCatalogService | None,
    ) -> None:
        self._catalogService = catalogService
        self._templateCatalogService = templateCatalogService

    def Reload(self) -> Tuple[List[CatalogItem], int, int]:
        self._catalogService.Reload()
        eventEntries = self._catalogService.GetEntries()

        templateEntries = []
        if self._templateCatalogService is not None:
            self._templateCatalogService.Reload()
            templateEntries = self._templateCatalogService.GetEntries()

        merged: List[CatalogItem] = []
        for entry in eventEntries:
            if bool(getattr(entry.definition, "hidden", False)):
                continue
            merged.append(CatalogItem("event", entry))
        for entry in templateEntries:
            if bool(getattr(entry.definition, "hidden", False)):
                continue
            merged.append(CatalogItem("template", entry))

        merged.sort(key=lambda item: str(item.entry.definition.label).lower())
        return merged, len(eventEntries), len(templateEntries)
