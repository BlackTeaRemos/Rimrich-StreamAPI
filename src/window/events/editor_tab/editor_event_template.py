from __future__ import annotations

from typing import Callable, Dict, List

from src.window.events.editor_tab.parameters.editor_template_parameter import EditorTemplateParameter


class EditorEventTemplate:
    def __init__(
        self,
        templateId: str,
        title: str,
        description: str,
        buildParameters: Callable[[], List[EditorTemplateParameter]],
        buildDocument: Callable[[Dict[str, object]], Dict[str, object]],
    ) -> None:
        self.templateId = str(templateId)
        self.title = str(title)
        self.description = str(description)
        self._buildParameters = buildParameters
        self._buildDocument = buildDocument

    def BuildParameters(self) -> List[EditorTemplateParameter]:
        return list(self._buildParameters())

    def BuildDocument(self, values: Dict[str, object]) -> Dict[str, object]:
        return dict(self._buildDocument(values))
