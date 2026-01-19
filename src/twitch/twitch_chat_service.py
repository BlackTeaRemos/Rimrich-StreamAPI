import asyncio
from threading import Thread
from typing import Optional

from src.events.chat_message_event import ChatMessageEvent
from src.core.events.event_bus import EventBus
from src.events.twitch_status_event import TwitchStatusEvent
from src.settings.app_settings import AppSettings
from src.core.settings.settings_service import SettingsService
from src.twitch.twitch_chat_client import TwitchChatClient


class TwitchChatService:
    """Start and stop Twitch chat listening in a background thread.

    Args:
        settingsService (SettingsService): settings manager.
        eventBus (EventBus): shared event bus.
    """

    def __init__(self, settingsService: SettingsService, eventBus: EventBus) -> None:
        self.settingsService = settingsService  # settings provider
        self.eventBus = eventBus  # shared bus
        self._thread: Optional[Thread] = None  # background thread
        self._loop: Optional[asyncio.AbstractEventLoop] = None  # async loop
        self._client: Optional[TwitchChatClient] = None  # twitch client

    def Start(self) -> None:
        """Launch the Twitch listener if configuration is present.

        Returns:
            None
        """

        settings = self.settingsService.Get()
        if not self.__HasConfig(settings):
            print("Twitch config missing for chat connect")
            try:
                self.eventBus.Publish(TwitchStatusEvent("missing_config", "Twitch config missing (open Settings)"))
            except Exception:
                pass
            return
        self.Stop()
        print("Starting twitch chat listener")
        try:
            self.eventBus.Publish(TwitchStatusEvent("connecting", f"Connecting to {settings.twitchChannel}"))
        except Exception:
            pass
        self._thread = Thread(target=self.__RunClient, daemon=True)
        self._thread.start()

    def Stop(self) -> None:
        """Shut down the Twitch listener and perform cleanup.

        Returns:
            None
        """

        loop = self._loop
        thread = self._thread
        client = self._client

        if loop is None:
            self._thread = None
            self._client = None
            return

        try:
            if client is not None and (not loop.is_closed()) and loop.is_running():
                asyncio.run_coroutine_threadsafe(self.__SafeCloseClient(client), loop).result(timeout=15)
        except Exception:
            pass

        try:
            if not loop.is_closed():
                loop.call_soon_threadsafe(loop.stop)
        except Exception:
            pass

        if thread is not None:
            try:
                thread.join(timeout=5)
            except Exception:
                pass

        # Clear fields after the background thread has had a chance to run its cleanup.
        self._loop = None
        self._thread = None
        self._client = None

        try:
            self.eventBus.Publish(TwitchStatusEvent("stopped", "Twitch stopped"))
        except Exception:
            pass

    async def __SafeCloseClient(self, client: TwitchChatClient) -> None:
        try:
            await client.close()
        except Exception:
            pass

        # Best-effort cleanup for cases where twitchio doesn't close its aiohttp session.
        try:
            httpClient = getattr(client, "http", None) or getattr(client, "_http", None)
            session = None
            if httpClient is not None:
                session = getattr(httpClient, "session", None) or getattr(httpClient, "_session", None)
            if session is not None and bool(getattr(session, "closed", False)) is False:
                await session.close()
        except Exception:
            pass

    def Restart(self) -> None:
        """Restart the listener to apply updated settings.

        Returns:
            None
        """

        self.Start()

    def SendMessage(self, content: str) -> None:
        """Send a message to the connected Twitch channel.

        Args:
            content: The message content to send.
        """
        loop = self._loop
        client = self._client

        if loop is None or client is None:
            print("TwitchChatService: Cannot send message - not connected")
            return

        try:
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(client.SendMessageAsync(content), loop)
            else:
                print("TwitchChatService: Cannot send message - event loop not running")
        except Exception as error:
            print(f"TwitchChatService: Failed to send message: {error}")

    def __RunClient(self) -> None:
        """Build an asyncio loop and run the Twitch chat client inside it.

        Returns:
            None
        """

        settings = self.settingsService.Get()
        loop: Optional[asyncio.AbstractEventLoop] = None
        client: Optional[TwitchChatClient] = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            client = TwitchChatClient(
                settings.twitchToken,
                settings.twitchNick,
                settings.twitchChannel,
                self.__HandleMessage,
                onStatus=self.__HandleStatus,
            )
            self._loop = loop
            self._client = client
            loop.run_until_complete(client.start())
        except Exception as error:
            print(f"Twitch client failed: {error}")
            try:
                self.eventBus.Publish(TwitchStatusEvent("error", str(error)))
            except Exception:
                pass
            pass
        finally:
            if loop is not None:
                try:
                    if client is not None:
                        loop.run_until_complete(self.__SafeCloseClient(client))
                    pending = asyncio.all_tasks(loop=loop)
                    for task in pending:
                        task.cancel()
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    loop.run_until_complete(loop.shutdown_asyncgens())
                except Exception:
                    pass
                try:
                    loop.close()
                except Exception:
                    pass

    def __HandleStatus(self, status: str, message: str) -> None:
        try:
            self.eventBus.Publish(TwitchStatusEvent(status, message))
        except Exception:
            pass

    def __HandleMessage(self, user: str, content: str) -> None:
        """Publish an incoming chat message to the event bus.

        Args:
            user (str): author name, e.g. "viewer".
            content (str): chat text, e.g. "hello".

        Returns:
            None
        """

        self.eventBus.Publish(ChatMessageEvent(user, content))

    def __HasConfig(self, settings: AppSettings) -> bool:
        """Validate the Twitch configuration is complete and usable.

        Args:
            settings (AppSettings): application settings.

        Returns:
            bool: True when configuration includes token, nick and channel.
        """

        return bool(settings.twitchToken and settings.twitchNick and settings.twitchChannel)
