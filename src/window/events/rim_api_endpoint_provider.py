from __future__ import annotations

from typing import Tuple

from src.core.settings.settings_service import SettingsService


class RimApiEndpointProvider:
    def __init__(self, settingsService: SettingsService) -> None:
        self._settingsService = settingsService

    def GetEndpoint(self) -> Tuple[str, int]:
        try:
            settings = self._settingsService.Get()
            host = str(getattr(settings, "rimApiHost", "localhost") or "localhost")
            port = int(getattr(settings, "rimApiPort", 0) or 0)
            return host, port
        except Exception:
            return "localhost", 0
