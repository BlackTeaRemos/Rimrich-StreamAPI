from src.events.chat_message_event import ChatMessageEvent
from src.core.events.event_bus import EventBus
from src.window.chat_window_service import ChatWindowService


class ChatEventListener:
    """Subscribe to chat events and update the chat log.

    Args:
        eventBus (EventBus): shared event bus.
        chatWindow (ChatWindowService): chat log window.
    """

    def __init__(self, eventBus: EventBus, chatWindow: ChatWindowService) -> None:
        self.eventBus = eventBus  # shared event bus
        self.chatWindow = chatWindow  # chat log window

    def Register(self) -> None:
        """Subscribe to ChatMessageEvent.

        Attaches the handler that records incoming chat messages.

        Args:
            None

        Returns:
            None
        """

        self.eventBus.Subscribe(ChatMessageEvent, self.OnChatMessage)

    def OnChatMessage(self, event: ChatMessageEvent) -> None:
        """Record an incoming chat message.

        Args:
            event (ChatMessageEvent): chat payload.

        Returns:
            None
        """

        try:
            self.chatWindow.RecordMessage(event.user, event.content)
        except Exception:
            pass
