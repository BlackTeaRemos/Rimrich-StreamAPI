from __future__ import annotations

from typing import Optional


class BusyButtonOverlay:
    def __init__(self, button: object, barHeight: int = 3, style: str = "Busy.Horizontal.TProgressbar") -> None:
        self._button = button
        self._barHeight = int(barHeight) if int(barHeight) > 0 else 3
        self._style = str(style or "")

        self._progressbar: object | None = None
        self._isRunning = False

        self.__EnsureBarCreated()
        self.__BindRepositionEvents()

    def Start(self) -> None:
        if self._isRunning:
            return
        self._isRunning = True

        bar = self._progressbar
        if bar is None:
            return

        self.__Reposition()

        try:
            startMethod = getattr(bar, "start", None)
            if callable(startMethod):
                startMethod(10)
        except Exception:
            pass

    def Stop(self) -> None:
        if not self._isRunning:
            return
        self._isRunning = False

        bar = self._progressbar
        if bar is None:
            return

        try:
            stopMethod = getattr(bar, "stop", None)
            if callable(stopMethod):
                stopMethod()
        except Exception:
            pass

        try:
            placeForgetMethod = getattr(bar, "place_forget", None)
            if callable(placeForgetMethod):
                placeForgetMethod()
        except Exception:
            pass

    def __EnsureBarCreated(self) -> None:
        if self._progressbar is not None:
            return

        button = self._button

        try:
            master = getattr(button, "master", None)
            if master is None:
                return
        except Exception:
            return

        try:
            from tkinter import ttk

            kwargs = {
                "mode": "indeterminate",
                "style": self._style,
                "length": 10,
            }
            self._progressbar = ttk.Progressbar(master, **kwargs)
        except Exception:
            self._progressbar = None

    def __BindRepositionEvents(self) -> None:
        button = self._button

        try:
            bindMethod = getattr(button, "bind", None)
            if callable(bindMethod):
                bindMethod("<Configure>", lambda event: self.__Reposition(), add="+")
        except Exception:
            pass

        try:
            master = getattr(button, "master", None)
            bindMethod = getattr(master, "bind", None)
            if callable(bindMethod):
                bindMethod("<Configure>", lambda event: self.__Reposition(), add="+")
        except Exception:
            pass

    def __Reposition(self) -> None:
        if not self._isRunning:
            return

        button = self._button
        bar = self._progressbar
        if bar is None:
            return

        try:
            viewableMethod = getattr(button, "winfo_viewable", None)
            if callable(viewableMethod) and not bool(viewableMethod()):
                return
        except Exception:
            return

        try:
            master = getattr(button, "master", None)
            if master is None:
                return
        except Exception:
            return

        try:
            masterUpdate = getattr(master, "update_idletasks", None)
            if callable(masterUpdate):
                masterUpdate()
        except Exception:
            pass

        try:
            buttonX = int(getattr(button, "winfo_x")())
            buttonY = int(getattr(button, "winfo_y")())
            buttonWidth = int(getattr(button, "winfo_width")())
            buttonHeight = int(getattr(button, "winfo_height")())
        except Exception:
            return

        if buttonWidth <= 0 or buttonHeight <= 0:
            return

        barX = buttonX
        barY = buttonY + max(0, buttonHeight - self._barHeight)

        try:
            placeMethod = getattr(bar, "place", None)
            if callable(placeMethod):
                placeMethod(x=barX, y=barY, width=buttonWidth, height=self._barHeight)
        except Exception:
            return

        try:
            liftMethod = getattr(bar, "lift", None)
            if callable(liftMethod):
                liftMethod()
        except Exception:
            pass
