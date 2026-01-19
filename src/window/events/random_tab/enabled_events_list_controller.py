from __future__ import annotations

import tkinter as tk
from typing import Callable, List

from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.game_events.game_event_definition import GameEventDefinition
from src.game_events.templates.game_event_template_catalog_service import GameEventTemplateCatalogService
from src.game_events.templates.game_event_template_definition import GameEventTemplateDefinition
from src.window.events.random_tab.enabled_events_list_state import EnabledEventsListState
from src.window.events.random_tab.enabled_events_list_view import EnabledEventsListView
from src.core.localization.localizer import Localizer


class EnabledEventsListController:
    def __init__(
        self,
        catalogService: GameEventCatalogService,
        templateCatalogService: GameEventTemplateCatalogService | None,
        getSelectedTags: Callable[[], List[str]],
        localizer: Localizer | None = None,
    ) -> None:
        self._catalogService = catalogService
        self._templateCatalogService = templateCatalogService
        self._getSelectedTags = getSelectedTags

        self._view = EnabledEventsListView(localizer=localizer)
        self._state = EnabledEventsListState()
        self._rows = []

    def Build(self, parent: tk.Frame) -> None:
        self._view.Build(
            parent,
            onFilterChanged=lambda: self.__Render(preserveSelection=True),
            onSelectionChanged=self.__OnSelectionChanged,
            onMouseWheel=self.__OnEnabledMouseWheel,
            onToggleRequested=self.__OnEnabledToggleRequested,
        )
        self.UpdateEnabledEvents()

    def Close(self) -> None:
        self._view.Close()
        self._state.Close()
        self._rows = []

    def UpdateEnabledEvents(self) -> None:
        preservedSelection = self._state.GetPreferredSelection()
        listbox = self._view.GetListbox()
        if listbox is not None and preservedSelection is None:
            try:
                selection = listbox.curselection()
                if selection and hasattr(self._view, "_itemKeys"):
                    selectedIndex = int(selection[0])
                    itemKeys = getattr(self._view, "_itemKeys", [])
                    if 0 <= selectedIndex < len(itemKeys):
                        preservedSelection = itemKeys[selectedIndex]
            except Exception:
                preservedSelection = None

        selectedTags = {str(value).strip() for value in self._getSelectedTags() if str(value).strip()}

        allDefinitions, allTemplates = self.__GetVisibleDefinitionsAndTemplates()

        rows = self._state.BuildRows(allDefinitions, allTemplates, selectedTags)
        self._rows = rows
        self.__Render(preserveSelection=True, preferredSelection=preservedSelection)

    def __Render(self, preserveSelection: bool = False, preferredSelection: tuple[str, str] | None = None) -> None:
        selection = preferredSelection or self._state.GetPreferredSelection()
        self._view.Render(self._rows, selection, preserveScroll=preserveSelection)

    def __OnSelectionChanged(self, selection: tuple[str, str] | None) -> None:
        if selection == self._state.GetPreferredSelection():
            return
        self._state.SetPreferredSelection(selection)
        self.__Render(preserveSelection=True, preferredSelection=selection)

    def GetEnabledDefinitionsAndTemplates(self) -> tuple[List[GameEventDefinition], List[GameEventTemplateDefinition]]:
        selectedTags = {str(value).strip() for value in self._getSelectedTags() if str(value).strip()}

        definitions, templates = self.__GetVisibleDefinitionsAndTemplates()

        return self._state.GetEnabled(definitions, templates, selectedTags)

    def __GetVisibleDefinitionsAndTemplates(self) -> tuple[List[GameEventDefinition], List[GameEventTemplateDefinition]]:
        definitions = [definition for definition in self._catalogService.GetAll() if not bool(getattr(definition, "hidden", False))]

        templates: List[GameEventTemplateDefinition] = []
        if self._templateCatalogService is not None:
            try:
                templates = [template for template in self._templateCatalogService.GetAll() if not bool(getattr(template, "hidden", False))]
            except Exception:
                templates = []

        return definitions, templates

    def __OnEnabledMouseWheel(self, event: tk.Event) -> str | None:
        listbox = self._view.GetListbox()
        if listbox is None:
            return None

        delta = getattr(event, "delta", 0)
        if isinstance(delta, int) and delta != 0:
            units = int(-delta / 120)
            if units == 0:
                units = -1 if delta > 0 else 1
            listbox.yview_scroll(units, "units")
            return "break"

        button = getattr(event, "num", None)
        if button == 4:
            listbox.yview_scroll(-3, "units")
            return "break"
        if button == 5:
            listbox.yview_scroll(3, "units")
            return "break"

        return None

    def __OnEnabledToggleRequested(self, event: tk.Event) -> str | None:
        listbox = self._view.GetListbox()
        if listbox is None:
            return None

        index = None
        try:
            if hasattr(event, "y"):
                index = int(listbox.nearest(int(event.y)))
        except Exception:
            index = None

        if index is None:
            selection = listbox.curselection()
            if not selection:
                return None
            index = int(selection[0])

        itemKeys = getattr(self._view, "_itemKeys", [])
        if index < 0 or index >= len(itemKeys):
            return None

        kind, identifier = itemKeys[index]

        selectedTags = {str(value).strip() for value in self._getSelectedTags() if str(value).strip()}
        tagEnabled = True
        if selectedTags:
            definitions, templates = self.__GetVisibleDefinitionsAndTemplates()
            if kind == "event":
                definition = next((item for item in definitions if item.eventId == identifier), None)
                tagEnabled = bool(definition) and bool(selectedTags.intersection({str(tag).strip() for tag in (definition.tags if definition is not None else []) if str(tag).strip()}))
            else:
                template = next((item for item in templates if item.templateId == identifier), None)
                tagEnabled = bool(template) and bool(selectedTags.intersection({str(tag).strip() for tag in (template.tags if template is not None else []) if str(tag).strip()}))

        self._state.Toggle(kind, identifier, tagEnabled)
        self.UpdateEnabledEvents()
        return "break"
