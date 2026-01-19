from pathlib import Path

from src.game_events.templates.game_event_template_definition import GameEventTemplateDefinition


class GameEventTemplateEntry:
    def __init__(self, definition: GameEventTemplateDefinition, filePath: Path) -> None:
        self.definition = definition
        self.filePath = filePath
