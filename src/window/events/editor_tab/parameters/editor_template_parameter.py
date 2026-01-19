from __future__ import annotations

import tkinter as tk
from abc import ABC, abstractmethod
from typing import Callable, Optional

from src.window.theme import Theme


class EditorTemplateParameter(ABC):
    def __init__(self, key: str, label: str, helpText: str | None = None) -> None:
        self.key = str(key)
        self.label = str(label)
        self.helpText = str(helpText) if helpText is not None else None

        self._rootWidget: tk.Widget | None = None

    @abstractmethod
    def Build(self, parent: tk.Frame, onChanged: Callable[[], None]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def GetValue(self) -> object:
        raise NotImplementedError()

    def Destroy(self) -> None:
        if self._rootWidget is None:
            return
        try:
            self._rootWidget.destroy()
        except Exception:
            pass
        self._rootWidget = None

    def _BuildRowContainer(self, parent: tk.Frame) -> tk.Frame:
        palette = Theme.Palette
        row = tk.Frame(parent, bg=palette.surface)
        row.pack(fill=tk.X, padx=8, pady=6)
        self._rootWidget = row
        return row
