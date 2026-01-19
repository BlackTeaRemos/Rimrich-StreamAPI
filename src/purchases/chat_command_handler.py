from typing import Optional

from src.purchases.chat_command_result import ChatCommandResult
from src.purchases.interfaces.balance_service_interface import BalanceServiceInterface
from src.purchases.interfaces.chat_command_handler_interface import ChatCommandHandlerInterface
from src.purchases.interfaces.purchase_service_interface import PurchaseServiceInterface


class ChatCommandHandler(ChatCommandHandlerInterface):
    """Handles chat commands for balance queries and event purchases."""

    COMMAND_PREFIX = "!"
    BALANCE_COMMANDS = ["silver", "balance", "money"]
    BUY_COMMANDS = ["buy", "purchase", "trigger", "event"]
    HELP_COMMANDS = ["shophelp", "buyhelp"]

    def __init__(
        self,
        balanceService: BalanceServiceInterface,
        purchaseService: PurchaseServiceInterface,
    ) -> None:
        self._balanceService = balanceService
        self._purchaseService = purchaseService

    def HandleMessage(self, username: str, content: str) -> Optional[ChatCommandResult]:
        """Process a chat message and execute any recognized commands.

        Args:
            username: The chat username.
            content: The message content.

        Returns:
            Optional[ChatCommandResult]: Result if a command was processed, None otherwise.
        """
        if not content or not content.strip():
            return None

        trimmedContent = content.strip()
        if not trimmedContent.startswith(self.COMMAND_PREFIX):
            return None

        commandText = trimmedContent[len(self.COMMAND_PREFIX):].strip()
        if not commandText:
            return None

        parts = commandText.split(maxsplit=1)
        commandName = parts[0].lower()
        commandArgument = parts[1].strip() if len(parts) > 1 else ""

        if commandName in self.BALANCE_COMMANDS:
            return self._HandleBalanceCommand(username)

        if commandName in self.BUY_COMMANDS:
            return self._HandleBuyCommand(username, commandArgument)

        if commandName in self.HELP_COMMANDS:
            return ChatCommandResult.Help()

        return None

    def _HandleBalanceCommand(self, username: str) -> ChatCommandResult:
        """Handle balance query command."""
        balance = self._balanceService.GetBalance(username)
        return ChatCommandResult.BalanceQuery(username, balance)

    def _HandleBuyCommand(self, username: str, eventIdentifier: str) -> ChatCommandResult:
        """Handle event purchase command."""
        if not eventIdentifier:
            return ChatCommandResult.PurchaseFailed(username, "Please specify an event. Usage: !buy <event_name>")

        purchaseResult = self._purchaseService.AttemptPurchase(username, eventIdentifier)

        if purchaseResult.success:
            return ChatCommandResult.PurchaseSuccess(
                username,
                purchaseResult.eventId,
                purchaseResult.cost,
                purchaseResult.newBalance,
            )
        else:
            return ChatCommandResult.PurchaseFailed(username, purchaseResult.message)
