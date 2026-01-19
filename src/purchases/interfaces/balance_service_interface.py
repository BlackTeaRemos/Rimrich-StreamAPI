from abc import ABC, abstractmethod


class BalanceServiceInterface(ABC):
    """Interface for managing user silver balances."""

    @abstractmethod
    def GetBalance(self, username: str) -> int:
        """Get the current silver balance for a user.

        Args:
            username: The chat username.

        Returns:
            int: Current silver balance.
        """
        pass

    @abstractmethod
    def AddSilver(self, username: str, amount: int) -> int:
        """Add silver to a user's balance.

        Args:
            username: The chat username.
            amount: Amount of silver to add.

        Returns:
            int: New balance after addition.
        """
        pass

    @abstractmethod
    def DeductSilver(self, username: str, amount: int) -> bool:
        """Deduct silver from a user's balance if sufficient funds exist.

        Args:
            username: The chat username.
            amount: Amount of silver to deduct.

        Returns:
            bool: True if deduction succeeded, False if insufficient funds.
        """
        pass

    @abstractmethod
    def Persist(self) -> None:
        """Save current balances to persistent storage."""
        pass

    @abstractmethod
    def GetAllBalances(self) -> dict[str, int]:
        """Get a copy of all user balances.

        Returns:
            dict[str, int]: Mapping of username to silver balance.
        """
        pass
