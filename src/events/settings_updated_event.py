from src.core.events.event import Event
from src.settings.app_settings import AppSettings


class SettingsUpdatedEvent(Event):

    def __init__(self, settings: AppSettings) -> None:
        super().__init__("settings_updated")
        self.settings = settings  # updated settings
