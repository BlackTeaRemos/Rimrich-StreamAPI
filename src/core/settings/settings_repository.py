import json
from pathlib import Path

from src.settings.app_settings import AppSettings


class SettingsRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def Load(self) -> AppSettings:
        try:
            if not self.path.exists():
                return AppSettings(False, "", "", "", False, 0, "localhost", 0, "en", True, 8080)
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                return AppSettings(
                    bool(data.get("borderless", False)),
                    str(data.get("twitchToken", "")),
                    str(data.get("twitchNick", "")),
                    str(data.get("twitchChannel", "")),
                    bool(data.get("chromaEnabled", False)),
                    int(data.get("chromaVoterCount", 0)),
                    str(data.get("rimApiHost", "localhost")),
                    int(data.get("rimApiPort", 0)),
                    str(data.get("uiLanguage", "en")),
                    bool(data.get("purchasesEnabled", True)),
                    int(data.get("purchasesWebPort", 8080)),
                )
        except Exception:
            return AppSettings(False, "", "", "", False, 0, "localhost", 0, "en", True, 8080)

    def Save(self, settings: AppSettings) -> None:
        try:
            payload = {
                "borderless": bool(settings.borderless),
                "twitchToken": str(settings.twitchToken),
                "twitchNick": str(settings.twitchNick),
                "twitchChannel": str(settings.twitchChannel),
                "chromaEnabled": bool(settings.chromaEnabled),
                "chromaVoterCount": int(settings.chromaVoterCount),
                "rimApiHost": str(getattr(settings, "rimApiHost", "localhost") or "localhost"),
                "rimApiPort": int(settings.rimApiPort),
                "uiLanguage": str(getattr(settings, "uiLanguage", "en") or "en"),
                "purchasesEnabled": bool(getattr(settings, "purchasesEnabled", True)),
                "purchasesWebPort": int(getattr(settings, "purchasesWebPort", 8080)),
            }
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle)
        except Exception:
            pass
