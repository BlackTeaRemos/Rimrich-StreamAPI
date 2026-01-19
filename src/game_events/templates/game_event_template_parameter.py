from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class GameEventTemplateParameter:
    name: str
    distribution: Dict[str, Any]
    description: str = ""

    @staticmethod
    def FromJson(name: str, document: Dict[str, Any]) -> "GameEventTemplateParameter":
        if not isinstance(document, dict):
            raise ValueError("Parameter definition must be an object")
        distribution = document.get("distribution", None)
        if distribution is None or not isinstance(distribution, dict):
            raise ValueError("Parameter missing required 'distribution' object")
        description = str(document.get("description", "") or "")
        return GameEventTemplateParameter(name=str(name), distribution=dict(distribution), description=description)
