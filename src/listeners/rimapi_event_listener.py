from src.events.app_exit_event import AppExitEvent
from src.events.chat_message_event import ChatMessageEvent
from src.core.events.event_bus import EventBus
from src.rimapi.rimapi_service import RimApiService


class RimApiEventListener:
    """Listen for chat and application exit events and forward them to RimApi service.

    Args:
        eventBus (EventBus): shared event bus.
        rimApiService (RimApiService): rimapi manager service.
    """

    def __init__(self, eventBus: EventBus, rimApiService: RimApiService) -> None:
        self.eventBus = eventBus  # shared bus
        self.rimApiService = rimApiService  # rimapi manager

    def Register(self) -> None:
        """Subscribe to chat and application exit events.

        Returns:
            None
        """

        self.eventBus.Subscribe(ChatMessageEvent, self.OnChatMessage)
        self.eventBus.Subscribe(AppExitEvent, self.OnAppExit)

    def OnChatMessage(self, event: ChatMessageEvent) -> None:
        """Forward chat messages to the RimApi service for processing.

        Args:
            event (ChatMessageEvent): chat payload containing user and content.

        Returns:
            None
        """

        try:
            self.rimApiService.HandleChat(event.user, event.content)
        except Exception:
            pass

    def OnAppExit(self, event: AppExitEvent) -> None:
        """Stop any active polls on application exit.

        Args:
            event (AppExitEvent): exit event payload.

        Returns:
            None
        """

        try:
            self.rimApiService.StopPoll()
        except Exception:
            pass
