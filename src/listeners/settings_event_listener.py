from src.core.events.event_bus import EventBus
from src.events.settings_updated_event import SettingsUpdatedEvent
from src.features.overlay.service import Service
from src.window.main_window_service import MainWindowService


class SettingsEventListener:
    """Apply settings updates to services such as overlay and main window.

    Args:
        eventBus (EventBus): shared event bus.
        overlayService (Service): overlay controller.
        mainWindow (MainWindowService): main window controller.
    """

    def __init__(self, eventBus: EventBus, overlayService: Service, mainWindow: MainWindowService) -> None:
        self.eventBus = eventBus  # shared event bus
        self.overlayService = overlayService  # overlay controller
        self.mainWindow = mainWindow  # main window controller

    def Register(self) -> None:
        """Subscribe to settings update events.

        Returns:
            None
        """

        self.eventBus.Subscribe(SettingsUpdatedEvent, self.OnSettingsUpdated)

    def OnSettingsUpdated(self, event: SettingsUpdatedEvent) -> None:
        """Apply relevant settings (e.g. borderless/chroma) to services.

        Args:
            event (SettingsUpdatedEvent): updated settings payload.

        Returns:
            None
        """

        try:
            self.overlayService.SetBorderless(event.settings.borderless)
            if self.mainWindow is not None:
                self.mainWindow.SetBorderlessOption(event.settings.borderless)
            self.overlayService.SetChroma(event.settings.chromaEnabled, event.settings.chromaVoterCount)
        except Exception:
            pass
