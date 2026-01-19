from typing import Callable, Optional

from twitchio import Client


class TwitchChatClient(Client):
    """Listen to a single Twitch channel and invoke provided callbacks.

    Args:
        token (str): oauth token, e.g. "oauth:token".
        nick (str): bot username, e.g. "mybot".
        channel (str): channel to join, e.g. "channel".
        onMessage (callable): callback for incoming chat lines: (user, content) -> None.
        onStatus (callable | None): optional status callback: (status, message) -> None.
    """

    def __init__(
        self,
        token: str,
        nick: str,
        channel: str,
        onMessage: Callable[[str, str], None],
        onStatus: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        self.onMessage = onMessage  # message callback
        self._onStatus = onStatus
        self._channel = channel  # channel name
        self._nick = nick  # provided nickname label
        self._connectedChannel = None  # reference to connected channel for sending
        super().__init__(token=token, initial_channels=[channel])

    async def event_ready(self) -> None:
        """Handle successful connection to Twitch and notify status callback.

        Returns:
            None
        """

        safeNick = self._nick if self._nick else getattr(self, "nick", "twitch")
        print(f"Twitch connected as {safeNick}")
        try:
            channel = self.get_channel(self._channel)
            if channel is not None:
                self._connectedChannel = channel
        except Exception:
            pass
        try:
            if self._onStatus is not None:
                self._onStatus("connected", f"Connected as {safeNick}")
        except Exception:
            pass

    async def event_disconnect(self) -> None:
        try:
            if self._onStatus is not None:
                self._onStatus("disconnected", "Disconnected")
        except Exception:
            pass

    async def event_message(self, message) -> None:
        """Forward incoming message payload to the configured message callback.

        Args:
            message (Message): twitch message payload.

        Returns:
            None
        """

        try:
            if getattr(message, "echo", False):
                return
            author = getattr(message, "author", None)
            userName = getattr(author, "name", "") if author is not None else ""
            text = getattr(message, "content", "")
            self.onMessage(userName, text)
        except Exception:
            pass

    async def SendMessageAsync(self, content: str) -> bool:
        """Send a message to the connected channel.

        Args:
            content: The message content to send.

        Returns:
            bool: True if message was sent successfully.
        """
        try:
            channel = self._connectedChannel
            if channel is None:
                channel = self.get_channel(self._channel)
            if channel is not None:
                await channel.send(content)
                return True
            return False
        except Exception as error:
            print(f"TwitchChatClient: Failed to send message: {error}")
            return False
