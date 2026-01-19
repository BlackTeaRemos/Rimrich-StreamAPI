from src.events.app_exit_event import AppExitEvent
from src.events.chat_message_event import ChatMessageEvent
from src.core.events.event_bus import EventBus
from src.voting.voting_service import VotingService


class VotingEventListener:
    def __init__(self, eventBus: EventBus, votingService: VotingService) -> None:
        self.eventBus = eventBus
        self.votingService = votingService

    def Register(self) -> None:
        self.eventBus.Subscribe(ChatMessageEvent, self.OnChatMessage)
        self.eventBus.Subscribe(AppExitEvent, self.OnAppExit)

    def OnChatMessage(self, event: ChatMessageEvent) -> None:
        try:
            self.votingService.HandleChat(event.user, event.content)
        except Exception:
            pass

    def OnAppExit(self, event: AppExitEvent) -> None:
        try:
            self.votingService.StopPoll()
        except Exception:
            pass
