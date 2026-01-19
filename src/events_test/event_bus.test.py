import sys
from pathlib import Path
import unittest

projectRoot = Path(__file__).resolve().parents[2]  # root directory
if str(projectRoot) not in sys.path:
    sys.path.append(str(projectRoot))

from src.events.app_started_event import AppStartedEvent
from src.core.events.event_bus import EventBus


class EventBusTestCase(unittest.TestCase):

    def TestPublishDeliversToSubscriber(self) -> None:
        eventBus = EventBus()
        received = {"count": 0}  # count of received events

        def OnStart(event: AppStartedEvent) -> None:
            received["count"] = received["count"] + 1

        eventBus.Subscribe(AppStartedEvent, OnStart)
        eventBus.Publish(AppStartedEvent())

        self.assertEqual(received["count"], 1)


if __name__ == "__main__":
    unittest.main()
