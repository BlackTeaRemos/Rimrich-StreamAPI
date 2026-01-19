from abc import ABC, abstractmethod
from typing import Optional

from src.purchases.chat_command_result import ChatCommandResult


class ChatCommandHandlerInterface(ABC):
    """Interface for handling chat commands related to purchases."""

    @abstractmethod
    def HandleMessage(self, username: str, content: str) -> Optional[ChatCommandResult]:
        """Process a chat message and execute any recognized commands.

        Args:
            username: The chat username.
            content: The message content.

        Returns:
            Optional[ChatCommandResult]: Result if a command was processed, None otherwise.
        """
        pass
