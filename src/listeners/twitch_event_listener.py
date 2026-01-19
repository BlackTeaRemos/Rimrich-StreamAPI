from src.events.app_exit_event import AppExitEvent
from src.events.app_started_event import AppStartedEvent
from src.core.events.event_bus import EventBus
from src.events.settings_updated_event import SettingsUpdatedEvent
from src.core.settings.settings_service import SettingsService
from src.twitch.twitch_chat_service import TwitchChatService


class TwitchEventListener:
    """Start and stop Twitch chat based on application lifecycle events.

    Args:
        eventBus (EventBus): shared event bus.
        twitchService (TwitchChatService): chat listener service.
        settingsService (SettingsService): settings provider.
    """

    def __init__(self, eventBus: EventBus, twitchService: TwitchChatService, settingsService: SettingsService) -> None:
        self.eventBus = eventBus  # shared bus
        self.twitchService = twitchService  # twitch chat service
        self.settingsService = settingsService  # settings provider

    def Register(self) -> None:
        """Subscribe to app lifecycle and settings events.

        Returns:
            None
        """

        self.eventBus.Subscribe(AppStartedEvent, self.OnAppStarted)
        self.eventBus.Subscribe(AppExitEvent, self.OnAppExit)
        self.eventBus.Subscribe(SettingsUpdatedEvent, self.OnSettingsUpdated)

    def OnAppStarted(self, event: AppStartedEvent) -> None:
        """Start Twitch chat listening when the application starts.

        Args:
            event (AppStartedEvent): startup event payload.

        Returns:
            None
        """

        self.twitchService.Start()

    def OnSettingsUpdated(self, event: SettingsUpdatedEvent) -> None:
        """Restart the Twitch listener to apply updated settings.

        Args:
            event (SettingsUpdatedEvent): updated settings payload.

        Returns:
            None
        """

        self.twitchService.Restart()

    def OnAppExit(self, event: AppExitEvent) -> None:
        """Stop Twitch chat listening on application exit.

        Args:
            event (AppExitEvent): exit event payload.

        Returns:
            None
        """

        self.twitchService.Stop()
