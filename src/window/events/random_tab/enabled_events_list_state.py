from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from src.game_events.game_event_definition import GameEventDefinition
from src.game_events.templates.game_event_template_definition import GameEventTemplateDefinition


@dataclass(frozen=True)
class EnabledEventRow:
    kind: str
    identifier: str
    label: str
    enabled: bool
    overridden: bool


class EnabledEventsListState:
    def __init__(self) -> None:
        self._eventEnabledOverrides: Dict[str, bool] = {}
        self._templateEnabledOverrides: Dict[str, bool] = {}
        self._preferredSelection: Tuple[str, str] | None = None

    def Close(self) -> None:
        self._eventEnabledOverrides = {}
        self._templateEnabledOverrides = {}
        self._preferredSelection = None

    def GetPreferredSelection(self) -> Tuple[str, str] | None:
        return self._preferredSelection

    def SetPreferredSelection(self, selection: Tuple[str, str] | None) -> None:
        self._preferredSelection = selection

    def BuildRows(
        self,
        definitions: List[GameEventDefinition],
        templates: List[GameEventTemplateDefinition],
        selectedTags: Set[str],
    ) -> List[EnabledEventRow]:
        rows: List[EnabledEventRow] = []

        for definition in definitions:
            tagEnabled = (not selectedTags) or bool(selectedTags.intersection({str(tag).strip() for tag in definition.tags if str(tag).strip()}))
            enabled = self._eventEnabledOverrides.get(definition.eventId, bool(tagEnabled))
            label = f"{definition.label}  ({definition.eventId})"
            overridden = definition.eventId in self._eventEnabledOverrides
            rows.append(EnabledEventRow("event", definition.eventId, label, enabled, overridden))

        for template in templates:
            tagEnabled = (not selectedTags) or bool(selectedTags.intersection({str(tag).strip() for tag in template.tags if str(tag).strip()}))
            enabled = self._templateEnabledOverrides.get(template.templateId, bool(tagEnabled))
            label = f"[T] {template.label}  ({template.templateId})"
            overridden = template.templateId in self._templateEnabledOverrides
            rows.append(EnabledEventRow("template", template.templateId, label, enabled, overridden))

        rows.sort(key=lambda value: value.label.lower())
        return rows

    def Toggle(self, kind: str, identifier: str, tagEnabled: bool) -> None:
        self._preferredSelection = (kind, identifier)

        if kind == "event":
            current = self._eventEnabledOverrides.get(identifier, bool(tagEnabled))
            newValue = not current
            if newValue == bool(tagEnabled):
                self._eventEnabledOverrides.pop(identifier, None)
            else:
                self._eventEnabledOverrides[identifier] = newValue
            return

        current = self._templateEnabledOverrides.get(identifier, bool(tagEnabled))
        newValue = not current
        if newValue == bool(tagEnabled):
            self._templateEnabledOverrides.pop(identifier, None)
        else:
            self._templateEnabledOverrides[identifier] = newValue

    def GetEnabled(
        self,
        definitions: List[GameEventDefinition],
        templates: List[GameEventTemplateDefinition],
        selectedTags: Set[str],
    ) -> tuple[List[GameEventDefinition], List[GameEventTemplateDefinition]]:
        if not selectedTags:
            enabledDefinitions = [definition for definition in definitions if self._eventEnabledOverrides.get(definition.eventId, True)]
            enabledTemplates = [template for template in templates if self._templateEnabledOverrides.get(template.templateId, True)]
            return enabledDefinitions, enabledTemplates

        enabledDefinitions: List[GameEventDefinition] = []
        for definition in definitions:
            tagEnabled = bool(selectedTags.intersection({str(tag).strip() for tag in definition.tags if str(tag).strip()}))
            enabled = self._eventEnabledOverrides.get(definition.eventId, tagEnabled)
            if enabled:
                enabledDefinitions.append(definition)

        enabledTemplates: List[GameEventTemplateDefinition] = []
        for template in templates:
            tagEnabled = bool(selectedTags.intersection({str(tag).strip() for tag in template.tags if str(tag).strip()}))
            enabled = self._templateEnabledOverrides.get(template.templateId, tagEnabled)
            if enabled:
                enabledTemplates.append(template)

        return enabledDefinitions, enabledTemplates
