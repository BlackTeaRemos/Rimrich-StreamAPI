from __future__ import annotations

from typing import Any, Dict

from src.core.localization.localization_table import LocalizationTable


class Localizer:
    def __init__(self, primary: LocalizationTable, fallback: LocalizationTable | None = None) -> None:
        self._primary = primary
        self._fallback = fallback

    @property
    def LanguageCode(self) -> str:
        return self._primary.LanguageCode

    def Text(self, key: str, **formatArgs: Any) -> str:
        value = self._primary.TryGet(key)
        if value is None and self._fallback is not None:
            value = self._fallback.TryGet(key)

        if value is None:
            value = str(key)

        if not formatArgs:
            return value

        try:
            return value.format(**formatArgs)
        except Exception:
            return value
