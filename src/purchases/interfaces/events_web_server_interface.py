from abc import ABC, abstractmethod


class EventsWebServerInterface(ABC):
    """Interface for the events listing web server."""

    @abstractmethod
    def Start(self, port: int) -> None:
        """Start the web server on the specified port.

        Args:
            port: The port number to listen on.
        """
        pass

    @abstractmethod
    def Stop(self) -> None:
        """Stop the web server."""
        pass

    @abstractmethod
    def IsRunning(self) -> bool:
        """Check if the web server is currently running.

        Returns:
            bool: True if running, False otherwise.
        """
        pass
