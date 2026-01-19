from pathlib import Path

from src.game_events.game_event_definition import GameEventDefinition


class GameEventEntry:
    def __init__(self, definition: GameEventDefinition, filePath: Path) -> None:
        self.definition = definition
        self.filePath = filePath
