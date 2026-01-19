from src.events.chat_message_event import ChatMessageEvent
from src.events.chat_command_response_event import ChatCommandResponseEvent
from src.core.events.event_bus import EventBus
from src.purchases.interfaces.balance_service_interface import BalanceServiceInterface
from src.purchases.interfaces.chat_command_handler_interface import ChatCommandHandlerInterface
from src.purchases.interfaces.silver_earning_service_interface import SilverEarningServiceInterface


class PurchaseEventListener:
    """Listens to chat events to award silver and process purchase commands."""

    def __init__(
        self,
        eventBus: EventBus,
        balanceService: BalanceServiceInterface,
        silverEarningService: SilverEarningServiceInterface,
        chatCommandHandler: ChatCommandHandlerInterface,
    ) -> None:
        self._eventBus = eventBus
        self._balanceService = balanceService
        self._silverEarningService = silverEarningService
        self._chatCommandHandler = chatCommandHandler
        self._processedVoters: set = set()

    def Register(self) -> None:
        """Register for chat message events."""
        self._eventBus.Subscribe(ChatMessageEvent, self._OnChatMessage)

    def _OnChatMessage(self, event: ChatMessageEvent) -> None:
        """Handle incoming chat messages - award silver and process commands."""
        username = event.user
        content = event.content

        if not username or not username.strip():
            return

        isVote = self._IsVoteMessage(content)
        if isVote:
            if username.lower() not in self._processedVoters:
                self._silverEarningService.OnPollVote(username)
                self._processedVoters.add(username.lower())
        else:
            self._silverEarningService.OnChatMessage(username)

        commandResult = self._chatCommandHandler.HandleMessage(username, content)
        if commandResult is not None:
            try:
                self._eventBus.Publish(ChatCommandResponseEvent(commandResult.responseMessage))
            except Exception as error:
                print(f"PurchaseEventListener: Failed to publish command response: {error}")

    def _IsVoteMessage(self, content: str) -> bool:
        """Check if message is a poll vote (single digit 1-4)."""
        trimmed = content.strip()
        return trimmed in ["1", "2", "3", "4"]

    def ResetVoterTracking(self) -> None:
        """Reset the voter tracking set (call when a new poll starts)."""
        self._processedVoters.clear()

    def PersistBalances(self) -> None:
        """Persist balances to storage."""
        try:
            self._balanceService.Persist()
        except Exception as error:
            print(f"PurchaseEventListener: Failed to persist balances: {error}")
