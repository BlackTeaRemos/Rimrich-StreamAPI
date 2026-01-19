from typing import Any, Dict, Optional


class GameEventRequest:
    def __init__(self, method: str, path: str, payload: str = "json", body: Optional[Dict[str, Any]] = None, query: Optional[Dict[str, str]] = None) -> None:
        self.method = (method or "GET").upper()
        self.path = path or "/"
        self.payload = payload or "json"  # json | query
        self.body = body or {}
        self.query = query or {}
