from __future__ import annotations

import os
from typing import Callable, List

from src.core.localization.localizer import Localizer
from src.window.events.catalog_item import CatalogItem
from src.window.events.catalog_tab import CatalogTab


class EventsCatalogActions:
    def __init__(
        self,
        catalogTab: CatalogTab,
        getItems: Callable[[], List[CatalogItem]],
        setStatus: Callable[[str], None],
        localizer: Localizer,
    ) -> None:
        self._catalogTab = catalogTab
        self._getItems = getItems
        self._setStatus = setStatus
        self._localizer = localizer

    def HandleSelectionChanged(self) -> None:
        items = self._getItems()

        index = self._catalogTab.GetSelectedIndex()
        if index is None:
            self._catalogTab.ClearDetails(self._localizer.Text("events.details.noEventSelected"))
            return
        if index < 0 or index >= len(items):
            self._catalogTab.ClearDetails(self._localizer.Text("events.details.noEventSelected"))
            return

        item = items[index]
        self._catalogTab.RenderDetailsText(item.ToDetailsText())

    def HandleOpenFile(self) -> None:
        items = self._getItems()

        index = self._catalogTab.GetSelectedIndex()
        if index is None or index < 0 or index >= len(items):
            self._setStatus(self._localizer.Text("events.status.noEventSelected"))
            return

        item = items[index]
        try:
            path = item.FilePathString()
            if hasattr(os, "startfile"):
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                import webbrowser

                webbrowser.open(items[index].entry.filePath.as_uri())
            self._setStatus(self._localizer.Text("events.status.opened", name=item.FileName()))
        except Exception as error:
            self._setStatus(self._localizer.Text("events.status.openFailed", error=str(error)))
