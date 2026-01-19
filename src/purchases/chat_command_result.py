class ChatCommandResult:
    """Result of a chat command execution."""

    def __init__(self, commandName: str, success: bool, responseMessage: str) -> None:
        self.commandName = commandName
        self.success = success
        self.responseMessage = responseMessage

    @staticmethod
    def BalanceQuery(username: str, balance: int) -> "ChatCommandResult":
        """Create a result for balance query."""
        return ChatCommandResult(
            commandName="balance",
            success=True,
            responseMessage=f"@{username}, you have {balance} silver.",
        )

    @staticmethod
    def PurchaseSuccess(username: str, eventLabel: str, cost: int, newBalance: int) -> "ChatCommandResult":
        """Create a result for successful purchase."""
        return ChatCommandResult(
            commandName="buy",
            success=True,
            responseMessage=f"@{username} triggered '{eventLabel}' for {cost} silver! Remaining: {newBalance}",
        )

    @staticmethod
    def PurchaseFailed(username: str, reason: str) -> "ChatCommandResult":
        """Create a result for failed purchase."""
        return ChatCommandResult(
            commandName="buy",
            success=False,
            responseMessage=f"@{username}, purchase failed: {reason}",
        )

    @staticmethod
    def UnknownCommand(commandName: str) -> "ChatCommandResult":
        """Create a result for unknown command."""
        return ChatCommandResult(
            commandName=commandName,
            success=False,
            responseMessage=f"Unknown command: {commandName}",
        )

    @staticmethod
    def Help() -> "ChatCommandResult":
        """Create a help response."""
        return ChatCommandResult(
            commandName="help",
            success=True,
            responseMessage="Commands: !silver (balance), !buy <event> (purchase event)",
        )
