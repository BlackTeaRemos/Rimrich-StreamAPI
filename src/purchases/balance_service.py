from typing import Dict

from src.purchases.interfaces.balance_repository_interface import BalanceRepositoryInterface
from src.purchases.interfaces.balance_service_interface import BalanceServiceInterface


class BalanceService(BalanceServiceInterface):
    """In-memory balance management with periodic persistence."""

    def __init__(self, repository: BalanceRepositoryInterface) -> None:
        self._repository = repository
        self._balances: Dict[str, int] = {}
        self._dirty = False
        self._LoadFromStorage()

    def _LoadFromStorage(self) -> None:
        """Load balances from persistent storage into memory."""
        try:
            self._balances = self._repository.Load()
        except Exception as error:
            print(f"BalanceService: Failed to load balances: {error}")
            self._balances = {}

    def GetBalance(self, username: str) -> int:
        """Get the current silver balance for a user.

        Args:
            username: The chat username.

        Returns:
            int: Current silver balance.
        """
        normalizedUsername = self._NormalizeUsername(username)
        return self._balances.get(normalizedUsername, 0)

    def AddSilver(self, username: str, amount: int) -> int:
        """Add silver to a user's balance.

        Args:
            username: The chat username.
            amount: Amount of silver to add.

        Returns:
            int: New balance after addition.
        """
        if amount <= 0:
            return self.GetBalance(username)

        normalizedUsername = self._NormalizeUsername(username)
        currentBalance = self._balances.get(normalizedUsername, 0)
        newBalance = currentBalance + amount
        self._balances[normalizedUsername] = newBalance
        self._dirty = True
        return newBalance

    def DeductSilver(self, username: str, amount: int) -> bool:
        """Deduct silver from a user's balance if sufficient funds exist.

        Args:
            username: The chat username.
            amount: Amount of silver to deduct.

        Returns:
            bool: True if deduction succeeded, False if insufficient funds.
        """
        if amount <= 0:
            return True

        normalizedUsername = self._NormalizeUsername(username)
        currentBalance = self._balances.get(normalizedUsername, 0)

        if currentBalance < amount:
            return False

        self._balances[normalizedUsername] = currentBalance - amount
        self._dirty = True
        return True

    def Persist(self) -> None:
        """Save current balances to persistent storage."""
        if not self._dirty:
            return

        try:
            self._repository.Save(dict(self._balances))
            self._dirty = False
        except Exception as error:
            print(f"BalanceService: Failed to persist balances: {error}")

    def GetAllBalances(self) -> Dict[str, int]:
        """Get a copy of all user balances.

        Returns:
            Dict[str, int]: Mapping of username to silver balance.
        """
        return dict(self._balances)

    def _NormalizeUsername(self, username: str) -> str:
        """Normalize username to lowercase for consistent lookups."""
        return str(username or "").strip().lower()
