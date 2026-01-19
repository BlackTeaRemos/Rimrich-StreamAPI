from __future__ import annotations

from typing import List

from src.window.events.editor_tab.editor_event_template import EditorEventTemplate
from src.window.events.editor_tab.game_api_data_source import GameApiDataSource
from src.window.events.editor_tab.templates.template_loader import TemplateLoader


class EditorTemplateCatalog:
    def GetAll(self, dataSource: GameApiDataSource) -> List[EditorEventTemplate]:
        return TemplateLoader.LoadAll(dataSource)
