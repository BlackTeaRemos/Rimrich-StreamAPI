from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class GameEventTemplateRequest:
    method: str
    path: str
    payload: str
    bodyTemplate: Any
    queryTemplate: Any

    @staticmethod
    def FromJson(document: Dict[str, Any]) -> "GameEventTemplateRequest":
        if not isinstance(document, dict):
            raise ValueError("Request must be an object")

        method = str(document.get("method", "POST") or "POST").upper()
        path = str(document.get("path", "/") or "/")
        payload = str(document.get("payload", "json") or "json")
        bodyTemplate = document.get("body", {})
        queryTemplate = document.get("query", {})
        return GameEventTemplateRequest(method=method, path=path, payload=payload, bodyTemplate=bodyTemplate, queryTemplate=queryTemplate)
