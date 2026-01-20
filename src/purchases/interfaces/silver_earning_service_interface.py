from abc import ABC, abstractmethod

from src.purchases.models.silver_earning_configuration import SilverEarningConfiguration


class SilverEarningServiceInterface(ABC):
    """Interface for awarding silver to users based on activity."""

    @abstractmethod
    def GetConfiguration(self) -> SilverEarningConfiguration:
        """Get current silver earning configuration.

        Returns:
            SilverEarningConfiguration: Current configuration values.
        """
        pass

    @abstractmethod
    def UpdateConfiguration(self, configuration: SilverEarningConfiguration) -> SilverEarningConfiguration:
        """Update silver earning configuration.

        Args:
            configuration: New configuration values.

        Returns:
            SilverEarningConfiguration: Stored configuration values.
        """
        pass

    @abstractmethod
    def OnChatMessage(self, username: str) -> int:
        """Award silver for sending a chat message.

        Args:
            username: The chat username.

        Returns:
            int: Amount of silver earned.
        """
        pass

    @abstractmethod
    def OnPollVote(self, username: str) -> int:
        """Award silver for participating in a poll vote.

        Args:
            username: The chat username.

        Returns:
            int: Amount of silver earned.
        """
        pass
