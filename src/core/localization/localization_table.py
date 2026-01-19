from __future__ import annotations

from typing import Dict


class LocalizationTable:
    def __init__(self, languageCode: str, entries: Dict[str, str]) -> None:
        self._languageCode = str(languageCode or "").strip().lower() or "en"
        self._entries = dict(entries or {})

    @property
    def LanguageCode(self) -> str:
        return self._languageCode

    def TryGet(self, key: str) -> str | None:
        safeKey = str(key or "").strip()
        if safeKey == "":
            return None
        return self._entries.get(safeKey)
