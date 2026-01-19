from src.events.settings_updated_event import SettingsUpdatedEvent
from src.core.events.event_bus import EventBus
from src.settings.app_settings import AppSettings
from src.core.settings.settings_repository import SettingsRepository


class SettingsService:
    def __init__(self, repository: SettingsRepository, eventBus: EventBus) -> None:
        self.repository = repository
        self.eventBus = eventBus
        self._settings = self.repository.Load()

    def Get(self) -> AppSettings:
        return self._settings

    def UpdateBorderless(self, enabled: bool) -> None:
        self._settings.borderless = bool(enabled)
        self.repository.Save(self._settings)
        self.eventBus.Publish(SettingsUpdatedEvent(self._settings))

    def UpdateTwitch(self, token: str, nick: str, channel: str) -> None:
        self._settings.twitchToken = str(token)
        self._settings.twitchNick = str(nick)
        self._settings.twitchChannel = str(channel)
        self.repository.Save(self._settings)
        self.eventBus.Publish(SettingsUpdatedEvent(self._settings))

    def UpdateChroma(self, enabled: bool, voterCount: int) -> None:
        self._settings.chromaEnabled = bool(enabled)
        safeCount = int(voterCount)
        if safeCount < 0:
            safeCount = 0
        if safeCount > 3:
            safeCount = 3
        self._settings.chromaVoterCount = safeCount
        self.repository.Save(self._settings)
        self.eventBus.Publish(SettingsUpdatedEvent(self._settings))

    def UpdateRimApiPort(self, port: int) -> None:
        try:
            safePort = int(port)
            if safePort < 0:
                safePort = 0
            if safePort > 65535:
                safePort = 65535
        except Exception:
            safePort = 0
        self._settings.rimApiPort = safePort
        self.repository.Save(self._settings)
        self.eventBus.Publish(SettingsUpdatedEvent(self._settings))

    def UpdateRimApiEndpoint(self, host: str, port: int) -> None:
        safeHost = str(host or "").strip()
        if safeHost == "":
            safeHost = "localhost"

        try:
            safePort = int(port)
            if safePort < 0:
                safePort = 0
            if safePort > 65535:
                safePort = 65535
        except Exception:
            safePort = 0

        self._settings.rimApiHost = safeHost
        self._settings.rimApiPort = safePort
        self.repository.Save(self._settings)
        self.eventBus.Publish(SettingsUpdatedEvent(self._settings))

    def UpdateUiLanguage(self, languageCode: str) -> None:
        safeCode = str(languageCode or "").strip().lower() or "en"
        self._settings.uiLanguage = safeCode
        self.repository.Save(self._settings)
        self.eventBus.Publish(SettingsUpdatedEvent(self._settings))

    def PublishCurrent(self) -> None:
        self.eventBus.Publish(SettingsUpdatedEvent(self._settings))
