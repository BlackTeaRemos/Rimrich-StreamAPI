from abc import ABC, abstractmethod
from typing import Dict


class BalanceRepositoryInterface(ABC):
    """Interface for persistent storage of user balances."""

    @abstractmethod
    def Load(self) -> Dict[str, int]:
        """Load all user balances from storage.

        Returns:
            Dict[str, int]: Mapping of username to silver balance.
        """
        pass

    @abstractmethod
    def Save(self, balances: Dict[str, int]) -> None:
        """Save all user balances to storage.

        Args:
            balances: Mapping of username to silver balance.
        """
        pass
