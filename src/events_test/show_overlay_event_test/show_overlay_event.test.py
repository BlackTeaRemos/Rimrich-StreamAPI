import sys
from pathlib import Path
import unittest

projectRoot = Path(__file__).resolve().parents[3]
if str(projectRoot) not in sys.path:
    sys.path.append(str(projectRoot))

from src.events.show_overlay_event import ShowOverlayEvent


class ShowOverlayEventTestCase(unittest.TestCase):
    def testTrimsToTenEntries(self) -> None:
        manyVotes = [(f"Item {index}", index) for index in range(15)]
        event = ShowOverlayEvent(manyVotes, ["a", "b", "c", "d"])
        self.assertEqual(len(event.votes), 10)
        self.assertEqual(event.votes[0][0], "Item 0")
        self.assertEqual(event.name, "show_overlay")
        self.assertEqual(event.voters, ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
