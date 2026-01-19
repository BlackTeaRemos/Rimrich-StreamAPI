class PurchaseResult:
    """Result of a purchase attempt."""

    def __init__(self, success: bool, message: str, eventId: str = "", cost: int = 0, newBalance: int = 0) -> None:
        self.success = success
        self.message = message
        self.eventId = eventId
        self.cost = cost
        self.newBalance = newBalance

    @staticmethod
    def Success(eventId: str, cost: int, newBalance: int) -> "PurchaseResult":
        """Create a successful purchase result."""
        return PurchaseResult(
            success=True,
            message=f"Purchased '{eventId}' for {cost} silver. Remaining: {newBalance}",
            eventId=eventId,
            cost=cost,
            newBalance=newBalance,
        )

    @staticmethod
    def InsufficientFunds(eventId: str, cost: int, currentBalance: int) -> "PurchaseResult":
        """Create a result for insufficient funds."""
        return PurchaseResult(
            success=False,
            message=f"Not enough silver for '{eventId}'. Need {cost}, have {currentBalance}.",
            eventId=eventId,
            cost=cost,
            newBalance=currentBalance,
        )

    @staticmethod
    def EventNotFound(eventIdentifier: str) -> "PurchaseResult":
        """Create a result for event not found."""
        return PurchaseResult(
            success=False,
            message=f"Event '{eventIdentifier}' not found.",
            eventId="",
            cost=0,
            newBalance=0,
        )

    @staticmethod
    def ExecutionFailed(eventId: str, reason: str) -> "PurchaseResult":
        """Create a result for failed event execution."""
        return PurchaseResult(
            success=False,
            message=f"Failed to trigger '{eventId}': {reason}",
            eventId=eventId,
            cost=0,
            newBalance=0,
        )
