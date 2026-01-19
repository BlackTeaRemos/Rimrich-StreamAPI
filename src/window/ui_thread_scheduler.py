from __future__ import annotations

import threading
from queue import Empty, Queue
from typing import Callable, Optional


class UiThreadScheduler:
    def __init__(self) -> None:
        self._queue: Queue[Callable[[], None]] = Queue()
        self._root: object | None = None
        self._uiThreadIdent: int | None = None
        self._pollIntervalMs = 50
        self._running = False

    def Start(self, root: object, pollIntervalMs: int = 50) -> None:
        """Start begins polling the queue on the UI thread.

        Must be called from the thread that created the Tk root.
        """

        self._root = root
        self._uiThreadIdent = threading.get_ident()
        self._pollIntervalMs = int(pollIntervalMs) if int(pollIntervalMs) > 0 else 50
        self._running = True

        self.__SchedulePoll(0)

    def Stop(self) -> None:
        self._running = False

    def IsUiThread(self) -> bool:
        if self._uiThreadIdent is None:
            return True
        return threading.get_ident() == self._uiThreadIdent

    def Post(self, work: Callable[[], None]) -> None:
        """Post enqueues work to run on the UI thread."""

        if work is None:
            return
        self._queue.put(work)

    def __SchedulePoll(self, delayMs: int) -> None:
        if not self._running:
            return
        root = self._root
        if root is None:
            return

        # Avoid importing tkinter types; just rely on duck-typed `.after`.
        try:
            afterMethod = getattr(root, "after", None)
            if afterMethod is None:
                return
            afterMethod(int(delayMs), self.__Poll)  # type: ignore[misc]
        except Exception:
            return

    def __Poll(self) -> None:
        if not self._running:
            return

        # Drain queue without blocking.
        try:
            while True:
                work = self._queue.get_nowait()
                try:
                    work()
                except Exception:
                    pass
        except Empty:
            pass
        finally:
            self.__SchedulePoll(self._pollIntervalMs)
