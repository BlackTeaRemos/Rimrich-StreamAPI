from src.core.events.event import Event


class ChatMessageEvent(Event):
    def __init__(self, user: str, content: str) -> None:
        super().__init__("chat_message")
        self.user = user  # chat author name
        self.content = content  # chat text
