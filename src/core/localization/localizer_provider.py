from __future__ import annotations

from src.core.localization.localizer import Localizer
from src.core.localization.tables_en import BuildEnglishTable
from src.core.localization.tables_ru import BuildRussianTable
from src.core.settings.settings_service import SettingsService


class LocalizerProvider:
    def __init__(self, settingsService: SettingsService) -> None:
        self._settingsService = settingsService
        self._fallback = BuildEnglishTable()
        self._ru = BuildRussianTable()

    def Get(self) -> Localizer:
        settings = self._settingsService.Get()
        languageCode = str(getattr(settings, "uiLanguage", "en") or "en").strip().lower() or "en"

        if languageCode == "en":
            primary = self._fallback
        elif languageCode.startswith("ru"):
            primary = self._ru
        else:
            primary = self._fallback

        return Localizer(primary=primary, fallback=self._fallback)
