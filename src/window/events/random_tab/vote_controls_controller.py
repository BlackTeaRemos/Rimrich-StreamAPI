from __future__ import annotations

import tkinter as tk
from typing import Callable

from src.window.theme import Theme
from src.core.localization.localizer import Localizer


class VoteControlsController:
    def __init__(self, onToggle: Callable[[], None], defaultDurationSeconds: int = 30, localizer: Localizer | None = None) -> None:
        self._onToggle = onToggle
        self._defaultDurationSeconds = defaultDurationSeconds
        self._localizer = localizer

        self._durationVar: tk.IntVar | None = None
        self._timerVar: tk.StringVar | None = None
        self._startButton: tk.Button | None = None

    def Build(self, parent: tk.Frame) -> None:
        palette = Theme.Palette
        tk.Label(parent, text=self.__Text("events.random.controls.duration", default="Duration (sec)"), bg=palette.surface, fg=palette.text).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        self._durationVar = tk.IntVar(value=int(self._defaultDurationSeconds))
        tk.Spinbox(parent, from_=5, to=3600, width=6, textvariable=self._durationVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT, justify=tk.CENTER).pack(side=tk.LEFT)

        self._timerVar = tk.StringVar(value="00")
        tk.Label(parent, textvariable=self._timerVar, bg=palette.surface, fg=palette.textMuted, width=6, anchor="e").pack(side=tk.RIGHT)

        startButton = tk.Button(
            parent,
            text=self.__Text("events.random.controls.start", default="Start"),
            command=self._onToggle,
            bg=palette.accent,
            fg=palette.text,
            activebackground=palette.accentHover,
            activeforeground=palette.text,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            width=8,
        )
        Theme.TryAddHover(startButton, palette.accent, palette.accentHover)
        startButton.pack(side=tk.RIGHT, padx=(0, 10))
        self._startButton = startButton

    def Close(self) -> None:
        self._durationVar = None
        self._timerVar = None
        self._startButton = None

    def SetRunning(self, running: bool) -> None:
        if self._startButton is None:
            return
        self._startButton.config(
            text=self.__Text("events.random.controls.stop", default="Stop")
            if running
            else self.__Text("events.random.controls.start", default="Start")
        )

    def __Text(self, key: str, default: str, **formatArgs: object) -> str:
        if self._localizer is None:
            return default
        try:
            return self._localizer.Text(key, **formatArgs)
        except Exception:
            return default

    def GetDurationSeconds(self) -> int:
        seconds = int(self._defaultDurationSeconds)
        if self._durationVar is not None:
            try:
                seconds = int(self._durationVar.get())
            except Exception:
                seconds = int(self._defaultDurationSeconds)
        return max(5, min(seconds, 3600))

    def UpdateTimer(self, remainingSeconds: int) -> None:
        if self._timerVar is None:
            return
        if remainingSeconds <= 0:
            self._timerVar.set("00")
        else:
            self._timerVar.set(f"{remainingSeconds:02d}")
