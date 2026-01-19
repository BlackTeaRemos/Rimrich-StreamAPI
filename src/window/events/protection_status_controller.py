from __future__ import annotations

import threading
import time
import tkinter as tk
from typing import Callable, Tuple

from src.core.localization.localizer import Localizer
from src.window.rest_api_client import RestApiClient


class ProtectionStatusController:
    def __init__(self, apiClient: RestApiClient, getEndpoint: Callable[[], Tuple[str, int]], localizer: Localizer) -> None:
        self._apiClient = apiClient
        self._getEndpoint = getEndpoint
        self._localizer = localizer

        self._labelVar: tk.StringVar | None = None
        self._stopEvent: threading.Event | None = None
        self._workerThread: threading.Thread | None = None

    def Build(self, parent: tk.Misc, backgroundColor: str, textColor: str) -> tk.Label:
        self._labelVar = tk.StringVar(value=self._localizer.Text("protection.label.unknown"))
        label = tk.Label(
            parent,
            textvariable=self._labelVar,
            bg=backgroundColor,
            fg=textColor,
            font=("Segoe UI", 10),
        )
        return label

    def Start(self, window: tk.Misc) -> None:
        if self._stopEvent is not None:
            return

        stopEvent = threading.Event()
        self._stopEvent = stopEvent

        def setTextFromWorker(text: str) -> None:
            try:
                window.after(0, lambda: self.SetText(text))
            except Exception:
                return

        def workerLoop() -> None:
            while True:
                if stopEvent.is_set():
                    return

                host, port = self._getEndpoint()
                try:
                    response = self._apiClient.GetJson(host, port, "/api/protection")
                    setTextFromWorker(self._FormatProtectionStatus(response))
                except Exception as error:
                    setTextFromWorker(self._localizer.Text("protection.label.error", message=str(error)))
                stopEvent.wait(2.5)

        self._workerThread = threading.Thread(target=workerLoop, name="ProtectionStatusPoll", daemon=True)
        self._workerThread.start()

    def Stop(self) -> None:
        stopEvent = self._stopEvent
        if stopEvent is None:
            return

        try:
            stopEvent.set()
        except Exception:
            pass

        workerThread = self._workerThread

        self._stopEvent = None
        self._workerThread = None

        if workerThread is not None:
            try:
                workerThread.join(timeout=0.5)
            except Exception:
                return

    def SetText(self, text: str) -> None:
        labelVar = self._labelVar
        if labelVar is None:
            return

        try:
            labelVar.set(text)
        except Exception:
            return

    def _FormatProtectionStatus(self, response: object) -> str:
        if not isinstance(response, dict):
            return self._localizer.Text("protection.label.unknown")

        if response.get("success") is False:
            errorValue = response.get("error")
            message = str(errorValue).strip() if errorValue is not None else ""
            if not message:
                message = self._localizer.Text("protection.error.unavailable")
            return self._localizer.Text("protection.label.error", message=message)

        try:
            externalActive = bool(response.get("externalBadEventsActive") or False)
            allBadActive = bool(response.get("allBadIncidentsActive") or False)
            nowTick = int(response.get("nowTick") or 0)
            externalUntil = int(response.get("externalBadEventsUntilTick") or 0)
            allBadUntil = int(response.get("allBadIncidentsUntilTick") or 0)
        except Exception:
            return self._localizer.Text("protection.label.unknown")

        if not externalActive and not allBadActive:
            return self._localizer.Text("protection.label.off")

        if allBadActive:
            remainingTicks = max(0, allBadUntil - nowTick)
            remainingSeconds = remainingTicks // 60
            return self._localizer.Text("protection.label.allBad", seconds=remainingSeconds)

        remainingTicks = max(0, externalUntil - nowTick)
        remainingSeconds = remainingTicks // 60
        return self._localizer.Text("protection.label.external", seconds=remainingSeconds)
