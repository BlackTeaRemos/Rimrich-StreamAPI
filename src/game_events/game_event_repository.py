from pathlib import Path
from typing import List

from src.game_events.game_event_entry import GameEventEntry
from src.game_events.game_event_definition import GameEventDefinition
from src.game_events.jsonc_document_loader import JsoncDocumentLoader


class GameEventRepository:
    def __init__(self, directory: Path, loader: JsoncDocumentLoader) -> None:
        self._directory = directory
        self._loader = loader

    def LoadAll(self) -> List[GameEventEntry]:
        if not self._directory.exists() or not self._directory.is_dir():
            return []

        entries: List[GameEventEntry] = []
        for filePath in sorted(self._directory.glob("*.jsonc")):
            try:
                document = self._loader.Load(filePath)
                definition = GameEventDefinition.FromJson(document)
                entries.append(GameEventEntry(definition, filePath))
            except Exception:
                # Skip invalid definitions; keep the app running.
                continue

        # De-duplicate by id while preserving order.
        seen = set()
        unique: List[GameEventEntry] = []
        for entry in entries:
            if entry.definition.eventId in seen:
                continue
            seen.add(entry.definition.eventId)
            unique.append(entry)
        return unique
