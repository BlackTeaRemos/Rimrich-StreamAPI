from src.core.events.event import Event


class ChatCommandResponseEvent(Event):
    """Event requesting a response message be sent to chat."""

    def __init__(self, responseMessage: str) -> None:
        super().__init__("chat_command_response")
        self.responseMessage = responseMessage
