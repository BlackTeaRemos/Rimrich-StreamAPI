import json
from pathlib import Path
from typing import Dict

from src.purchases.interfaces.balance_repository_interface import BalanceRepositoryInterface


class BalanceRepository(BalanceRepositoryInterface):
    """File-based persistent storage for user silver balances."""

    def __init__(self, filePath: Path) -> None:
        self._filePath = filePath

    def Load(self) -> Dict[str, int]:
        """Load all user balances from the JSON file.

        Returns:
            Dict[str, int]: Mapping of username to silver balance.
        """
        if not self._filePath.exists():
            return {}

        try:
            content = self._filePath.read_text(encoding="utf-8")
            parsed = json.loads(content)
            if not isinstance(parsed, dict):
                return {}

            balances: Dict[str, int] = {}
            for username, balance in parsed.items():
                if isinstance(username, str) and username.strip():
                    normalizedUsername = username.strip().lower()
                    try:
                        balances[normalizedUsername] = int(balance)
                    except (ValueError, TypeError):
                        balances[normalizedUsername] = 0
            return balances
        except Exception as error:
            print(f"BalanceRepository: Failed to load balances: {error}")
            return {}

    def Save(self, balances: Dict[str, int]) -> None:
        """Save all user balances to the JSON file.

        Args:
            balances: Mapping of username to silver balance.
        """
        try:
            self._filePath.parent.mkdir(parents=True, exist_ok=True)
            content = json.dumps(balances, indent=2, ensure_ascii=False)
            self._filePath.write_text(content, encoding="utf-8")
        except Exception as error:
            print(f"BalanceRepository: Failed to save balances: {error}")
