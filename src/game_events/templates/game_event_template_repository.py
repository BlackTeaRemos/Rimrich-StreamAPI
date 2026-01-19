from pathlib import Path
from typing import List

from src.game_events.jsonc_document_loader import JsoncDocumentLoader
from src.game_events.templates.game_event_template_definition import GameEventTemplateDefinition
from src.game_events.templates.game_event_template_entry import GameEventTemplateEntry


class GameEventTemplateRepository:
    def __init__(self, directory: Path, loader: JsoncDocumentLoader) -> None:
        self._directory = directory
        self._loader = loader

    def LoadAll(self) -> List[GameEventTemplateEntry]:
        if not self._directory.exists() or not self._directory.is_dir():
            return []

        entries: List[GameEventTemplateEntry] = []
        for filePath in sorted(self._directory.glob("*.jsonc")):
            try:
                document = self._loader.Load(filePath)
                definition = GameEventTemplateDefinition.FromJson(document)
                entries.append(GameEventTemplateEntry(definition, filePath))
            except Exception:
                continue

        seen = set()
        unique: List[GameEventTemplateEntry] = []
        for entry in entries:
            if entry.definition.templateId in seen:
                continue
            seen.add(entry.definition.templateId)
            unique.append(entry)
        return unique
