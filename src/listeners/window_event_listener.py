from src.events.app_exit_event import AppExitEvent
from src.events.app_started_event import AppStartedEvent
from src.core.events.event_bus import EventBus
from src.window.main_window_service import MainWindowService


class WindowEventListener:
    """
    WindowEventListener registers callbacks for window lifecycle events

    Args:
        eventBus (EventBus): shared event bus example EventBus()
        windowService (MainWindowService): window controller example MainWindowService(EventBus(), BorderlessWindowService(EventBus()))

    Returns:
        WindowEventListener: configured listener example WindowEventListener(EventBus(), MainWindowService(EventBus(), BorderlessWindowService(EventBus())))
    """

    def __init__(self, eventBus: EventBus, windowService: MainWindowService) -> None:
        self.eventBus = eventBus  # shared event bus
        self.windowService = windowService  # service controlling window

    def Register(self) -> None:
        """
        Register attaches handlers to start and exit events

        Args:
            None: no arguments example None

        Returns:
            None: nothing returned example None
        """

        self.eventBus.Subscribe(AppStartedEvent, self.OnAppStarted)
        self.eventBus.Subscribe(AppExitEvent, self.OnAppExit)

    def OnAppStarted(self, event: AppStartedEvent) -> None:
        """
        OnAppStarted invokes window display when startup event arrives

        Args:
            event (AppStartedEvent): startup event example AppStartedEvent()

        Returns:
            None: nothing returned example None
        """

        self.windowService.ShowWindow()

    def OnAppExit(self, event: AppExitEvent) -> None:
        """
        OnAppExit closes the window on shutdown events

        Args:
            event (AppExitEvent): exit event example AppExitEvent()

        Returns:
            None: nothing returned example None
        """

        self.windowService.CloseWindow()
