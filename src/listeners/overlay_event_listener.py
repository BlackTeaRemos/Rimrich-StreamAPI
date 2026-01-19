from typing import Optional

from src.events.app_exit_event import AppExitEvent
from src.events.close_overlay_event import CloseOverlayEvent
from src.core.events.event_bus import EventBus
from src.events.show_overlay_event import ShowOverlayEvent
from src.core.settings.settings_service import SettingsService
from src.features.overlay.service import Service
from src.window.main_window_service import MainWindowService


class OverlayEventListener:
    """Register handlers for overlay show and close events.

    Args:
        eventBus (EventBus): shared event bus.
        overlayService (Service): overlay controller.
        mainWindow (Optional[MainWindowService]): optional main window used for preview updates.
        settingsService (Optional[SettingsService]): optional settings manager.
    """

    def __init__(self, eventBus: EventBus, overlayService: Service, mainWindow: Optional[MainWindowService], settingsService: Optional[SettingsService]) -> None:
        self.eventBus = eventBus  # shared event bus
        self.overlayService = overlayService  # overlay controller
        self.mainWindow = mainWindow  # optional preview target
        self.settingsService = settingsService  # optional settings manager

    def Register(self) -> None:
        """
        Register attaches handlers for overlay show and close events

        Args:
            None: no arguments example None

        Returns:
            None: nothing returned example None
        """

        self.eventBus.Subscribe(ShowOverlayEvent, self.OnShowOverlay)
        self.eventBus.Subscribe(CloseOverlayEvent, self.OnCloseOverlay)
        self.eventBus.Subscribe(AppExitEvent, self.OnCloseOverlay)

    def OnShowOverlay(self, event: ShowOverlayEvent) -> None:
        """
        OnShowOverlay requests the overlay service to render votes

        Args:
            event (ShowOverlayEvent): overlay request example ShowOverlayEvent([])

        Returns:
            None: nothing returned example None
        """

        self.overlayService.ShowWindow(event.votes, event.voters)
        if self.mainWindow is not None:
            try:
                self.mainWindow.UpdatePreview(event.votes)
            except Exception:
                pass

    def OnCloseOverlay(self, event: CloseOverlayEvent | AppExitEvent) -> None:
        """
        OnCloseOverlay closes the overlay window

        Args:
            event (CloseOverlayEvent | AppExitEvent): close request example CloseOverlayEvent()

        Returns:
            None: nothing returned example None
        """

        try:
            self.overlayService.CloseWindow()
        except Exception:
            pass
        if self.mainWindow is not None:
            try:
                self.mainWindow.ClearPreview()
            except Exception:
                pass
