from src.core.events.event_bus import EventBus
from src.events.twitch_status_event import TwitchStatusEvent
from src.window.chat_window_service import ChatWindowService
from src.window.main_window_service import MainWindowService


class TwitchStatusEventListener:
    def __init__(self, eventBus: EventBus, mainWindow: MainWindowService, chatWindow: ChatWindowService) -> None:
        self.eventBus = eventBus
        self.mainWindow = mainWindow
        self.chatWindow = chatWindow

    def Register(self) -> None:
        self.eventBus.Subscribe(TwitchStatusEvent, self.OnStatus)

    def OnStatus(self, event: TwitchStatusEvent) -> None:
        try:
            summary = event.message or event.status
            self.chatWindow.SetStatus(summary)
        except Exception:
            pass
        try:
            self.mainWindow.SetTwitchStatus(event.status, event.message)
        except Exception:
            pass
