from __future__ import annotations

import importlib
import pkgutil
from dataclasses import dataclass
from types import ModuleType
from typing import Callable, Iterable, List, Optional

from src.window.events.editor_tab.editor_event_template import EditorEventTemplate
from src.window.events.editor_tab.game_api_data_source import GameApiDataSource


BuildTemplatesFunction = Callable[[GameApiDataSource], List[EditorEventTemplate]]


@dataclass(frozen=True)
class LoadedTemplateModule:
    name: str
    module: ModuleType
    build_templates: Optional[BuildTemplatesFunction]


class TemplateLoader:
    @staticmethod
    def LoadAll(dataSource: GameApiDataSource) -> List[EditorEventTemplate]:
        templates: List[EditorEventTemplate] = []
        for loaded_module in TemplateLoader._DiscoverModules():
            if loaded_module.build_templates is None:
                continue
            try:
                templates.extend(list(loaded_module.build_templates(dataSource)))
            except Exception:
                # Best-effort: a single bad template module shouldn't break the whole editor.
                continue

        # Stable sort for nicer UX.
        templates.sort(key=lambda template: (template.title or template.templateId))
        return templates

    @staticmethod
    def _DiscoverModules() -> Iterable[LoadedTemplateModule]:
        package_name = "src.window.events.editor_tab.templates"
        package = importlib.import_module(package_name)

        for module_info in pkgutil.iter_modules(package.__path__, package.__name__ + "."):
            module_name = module_info.name

            # Skip private modules
            if module_name.rsplit(".", 1)[-1].startswith("_"):
                continue

            module = TemplateLoader._SafeImport(module_name)
            if module is None:
                continue

            build_function = getattr(module, "build_templates", None)
            if callable(build_function):
                yield LoadedTemplateModule(name=module_name, module=module, build_templates=build_function)
            else:
                yield LoadedTemplateModule(name=module_name, module=module, build_templates=None)

    @staticmethod
    def _SafeImport(module_name: str) -> Optional[ModuleType]:
        try:
            return importlib.import_module(module_name)
        except Exception:
            return None
