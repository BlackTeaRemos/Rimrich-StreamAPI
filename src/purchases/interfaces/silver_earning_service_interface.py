from abc import ABC, abstractmethod


class SilverEarningServiceInterface(ABC):
    """Interface for awarding silver to users based on activity."""

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
