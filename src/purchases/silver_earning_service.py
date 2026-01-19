import time
from typing import Dict

from src.purchases.interfaces.balance_service_interface import BalanceServiceInterface
from src.purchases.interfaces.silver_earning_service_interface import SilverEarningServiceInterface


class SilverEarningService(SilverEarningServiceInterface):
    """Awards silver to users based on chat activity and poll participation."""

    SILVER_PER_CHAT_MESSAGE = 5
    SILVER_PER_POLL_VOTE = 50
    CHAT_REWARD_COOLDOWN_SECONDS = 3.0

    def __init__(self, balanceService: BalanceServiceInterface) -> None:
        self._balanceService = balanceService
        self._lastChatRewardAtByUser: Dict[str, float] = {}

    def OnChatMessage(self, username: str) -> int:
        """Award silver for sending a chat message.

        Args:
            username: The chat username.

        Returns:
            int: Amount of silver earned.
        """
        if not username or not username.strip():
            return 0

        normalizedUsername = str(username).strip().lower()
        currentTime = time.monotonic()
        lastRewardAt = self._lastChatRewardAtByUser.get(normalizedUsername, 0.0)
        if currentTime - lastRewardAt < self.CHAT_REWARD_COOLDOWN_SECONDS:
            return 0

        self._lastChatRewardAtByUser[normalizedUsername] = currentTime
        earnedAmount = self.SILVER_PER_CHAT_MESSAGE
        self._balanceService.AddSilver(username, earnedAmount)
        return earnedAmount

    def OnPollVote(self, username: str) -> int:
        """Award silver for participating in a poll vote.

        Args:
            username: The chat username.

        Returns:
            int: Amount of silver earned.
        """
        if not username or not username.strip():
            return 0

        earnedAmount = self.SILVER_PER_POLL_VOTE
        self._balanceService.AddSilver(username, earnedAmount)
        return earnedAmount
