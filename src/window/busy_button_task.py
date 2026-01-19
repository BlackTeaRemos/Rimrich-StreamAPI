from __future__ import annotations

import threading
from typing import Callable, Generic, Optional, TypeVar

from src.window.busy_button_overlay import BusyButtonOverlay
from src.window.ui_thread_scheduler import UiThreadScheduler


TaskResult = TypeVar("TaskResult")


class BusyButtonTask(Generic[TaskResult]):
    def __init__(
        self,
        button: object,
        work: Callable[[], TaskResult],
        onSuccess: Callable[[TaskResult], None] | None = None,
        onError: Callable[[Exception], None] | None = None,
        uiScheduler: UiThreadScheduler | None = None,
        busyText: str | None = None,
    ) -> None:
        self._button = button
        self._work = work
        self._onSuccess = onSuccess
        self._onError = onError
        self._uiScheduler = uiScheduler
        self._busyText = busyText

        self._overlay = BusyButtonOverlay(button)
        self._isRunning = False
        self._originalText: str | None = None

    def Invoke(self) -> None:
        if self._isRunning:
            return
        self._isRunning = True

        self.__SetBusyUiState(True)

        def worker() -> None:
            try:
                result = self._work()
                self.__PostToUi(lambda: self.__FinishSuccess(result))
            except Exception as error:
                self.__PostToUi(lambda: self.__FinishError(error))

        threading.Thread(target=worker, name="BusyButtonTask", daemon=True).start()

    def __FinishSuccess(self, result: TaskResult) -> None:
        try:
            if self._onSuccess is not None:
                self._onSuccess(result)
        finally:
            self.__SetBusyUiState(False)

    def __FinishError(self, error: Exception) -> None:
        try:
            if self._onError is not None:
                self._onError(error)
        finally:
            self.__SetBusyUiState(False)

    def __PostToUi(self, work: Callable[[], None]) -> None:
        scheduler = self._uiScheduler
        if scheduler is not None:
            scheduler.Post(work)
            return

        try:
            afterMethod = getattr(self._button, "after", None)
            if callable(afterMethod):
                afterMethod(0, work)
        except Exception:
            pass

    def __SetBusyUiState(self, isBusy: bool) -> None:
        button = self._button

        if isBusy:
            try:
                currentText = getattr(button, "cget")("text")
                self._originalText = str(currentText)
            except Exception:
                self._originalText = None

            if self._busyText is not None:
                try:
                    getattr(button, "configure")(text=str(self._busyText))
                except Exception:
                    pass

            try:
                getattr(button, "configure")(state="disabled")
            except Exception:
                pass

            try:
                updateMethod = getattr(button, "update_idletasks", None)
                if callable(updateMethod):
                    updateMethod()
            except Exception:
                pass

            self._overlay.Start()
            return

        self._overlay.Stop()

        try:
            getattr(button, "configure")(state="normal")
        except Exception:
            pass

        if self._originalText is not None:
            try:
                getattr(button, "configure")(text=self._originalText)
            except Exception:
                pass

        self._isRunning = False
