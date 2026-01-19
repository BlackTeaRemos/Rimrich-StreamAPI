from src.events.chat_command_response_event import ChatCommandResponseEvent
from src.core.events.event_bus import EventBus
from src.twitch.twitch_chat_service import TwitchChatService


class ChatResponseEventListener:
    """Listens for chat command responses and sends them to Twitch."""

    def __init__(self, eventBus: EventBus, twitchService: TwitchChatService) -> None:
        self._eventBus = eventBus
        self._twitchService = twitchService

    def Register(self) -> None:
        """Register for chat command response events."""
        self._eventBus.Subscribe(ChatCommandResponseEvent, self._OnChatCommandResponse)

    def _OnChatCommandResponse(self, event: ChatCommandResponseEvent) -> None:
        """Handle chat command response - send message to Twitch."""
        try:
            responseMessage = event.responseMessage
            if responseMessage and responseMessage.strip():
                self._twitchService.SendMessage(responseMessage)
        except Exception as error:
            print(f"ChatResponseEventListener: Failed to send response: {error}")
