from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Literal, Union

from src.game_events.game_event_entry import GameEventEntry
from src.game_events.templates.game_event_template_entry import GameEventTemplateEntry


CatalogItemKind = Literal["event", "template"]
CatalogItemEntry = Union[GameEventEntry, GameEventTemplateEntry]


@dataclass(frozen=True)
class CatalogItem:
    kind: CatalogItemKind
    entry: CatalogItemEntry

    def Identifier(self) -> str:
        try:
            if self.kind == "event":
                return str(self.entry.definition.eventId)
            return str(self.entry.definition.templateId)
        except Exception:
            return ""

    def Label(self) -> str:
        try:
            return str(self.entry.definition.label)
        except Exception:
            return ""

    def DisplayText(self) -> str:
        label = self.Label()
        identifier = self.Identifier()
        if identifier:
            return f"{label}  [{identifier}]"
        return label

    def FilePathString(self) -> str:
        return str(self.entry.filePath)

    def FileName(self) -> str:
        return self.entry.filePath.name

    def ToDetailsText(self) -> str:
        return json.dumps(self.ToDetailsDocument(), indent=2)

    def ToDetailsDocument(self) -> Dict[str, Any]:
        if self.kind == "event":
            definition = self.entry.definition
            return {
                "type": "normal",
                "id": definition.eventId,
                "label": definition.label,
                "userMessage": getattr(definition, "userMessage", None),
                "hidden": bool(getattr(definition, "hidden", False)),
                "cost": definition.cost,
                "probability": definition.probability,
                "tags": definition.tags,
                "requests": [
                    {
                        "method": request.method,
                        "path": request.path,
                        "payload": request.payload,
                        "query": request.query,
                        "body": request.body,
                    }
                    for request in definition.requests
                ],
                "file": str(self.entry.filePath),
            }

        definition = self.entry.definition
        return {
            "type": "random",
            "id": definition.templateId,
            "label": definition.label,
            "userMessage": getattr(definition, "userMessage", None),
            "hidden": bool(getattr(definition, "hidden", False)),
            "cost": definition.cost,
            "probability": definition.probability,
            "tags": definition.tags,
            "parameters": [
                {
                    "name": parameter.name,
                    "description": parameter.description,
                    "distribution": parameter.distribution,
                }
                for parameter in definition.parameters
            ],
            "requests": [
                {
                    "method": request.method,
                    "path": request.path,
                    "payload": request.payload,
                    "queryTemplate": request.queryTemplate,
                    "bodyTemplate": request.bodyTemplate,
                }
                for request in definition.requests
            ],
            "file": str(self.entry.filePath),
        }
