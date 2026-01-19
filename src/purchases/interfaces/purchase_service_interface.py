from abc import ABC, abstractmethod
from typing import Optional

from src.purchases.purchase_result import PurchaseResult


class PurchaseServiceInterface(ABC):
    """Interface for processing event purchases."""

    @abstractmethod
    def AttemptPurchase(self, username: str, eventIdentifier: str) -> PurchaseResult:
        """Attempt to purchase and trigger an event.

        Args:
            username: The chat username making the purchase.
            eventIdentifier: The event ID or label to purchase.

        Returns:
            PurchaseResult: Result containing success/failure and message.
        """
        pass
