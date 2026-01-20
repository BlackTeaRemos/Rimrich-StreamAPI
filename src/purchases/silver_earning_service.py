import time
from typing import Dict

from src.purchases.interfaces.balance_service_interface import BalanceServiceInterface
from src.purchases.interfaces.silver_earning_service_interface import SilverEarningServiceInterface
from src.purchases.models.silver_earning_configuration import SilverEarningConfiguration


class SilverEarningService(SilverEarningServiceInterface):
    """Awards silver to users based on chat activity and poll participation."""

    SILVER_PER_CHAT_MESSAGE = 5
    SILVER_PER_POLL_VOTE = 50
    CHAT_REWARD_COOLDOWN_SECONDS = 3.0

    def __init__(self, balanceService: BalanceServiceInterface) -> None:
        self._balanceService = balanceService
        self._lastChatRewardAtByUser: Dict[str, float] = {}
        self._silverPerChatMessage = int(self.SILVER_PER_CHAT_MESSAGE)
        self._silverPerPollVote = int(self.SILVER_PER_POLL_VOTE)
        self._chatRewardCooldownSeconds = float(self.CHAT_REWARD_COOLDOWN_SECONDS)

    def GetConfiguration(self) -> SilverEarningConfiguration:
        return SilverEarningConfiguration(
            silverPerChatMessage=self._silverPerChatMessage,
            silverPerPollVote=self._silverPerPollVote,
            chatRewardCooldownSeconds=self._chatRewardCooldownSeconds,
        )

    def UpdateConfiguration(self, configuration: SilverEarningConfiguration) -> SilverEarningConfiguration:
        normalized = self._NormalizeConfiguration(configuration)
        self._silverPerChatMessage = normalized.silverPerChatMessage
        self._silverPerPollVote = normalized.silverPerPollVote
        self._chatRewardCooldownSeconds = normalized.chatRewardCooldownSeconds
        return normalized

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
        if currentTime - lastRewardAt < self._chatRewardCooldownSeconds:
            return 0

        self._lastChatRewardAtByUser[normalizedUsername] = currentTime
        earnedAmount = self._silverPerChatMessage
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

        earnedAmount = self._silverPerPollVote
        self._balanceService.AddSilver(username, earnedAmount)
        return earnedAmount

    def _NormalizeConfiguration(self, configuration: SilverEarningConfiguration) -> SilverEarningConfiguration:
        chatAmount = int(configuration.silverPerChatMessage)
        pollAmount = int(configuration.silverPerPollVote)
        cooldownSeconds = float(configuration.chatRewardCooldownSeconds)
        if chatAmount < 0:
            chatAmount = 0
        if pollAmount < 0:
            pollAmount = 0
        if cooldownSeconds < 0:
            cooldownSeconds = 0.0
        return SilverEarningConfiguration(
            silverPerChatMessage=chatAmount,
            silverPerPollVote=pollAmount,
            chatRewardCooldownSeconds=cooldownSeconds,
        )
