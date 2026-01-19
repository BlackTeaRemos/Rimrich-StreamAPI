from __future__ import annotations

import tkinter as tk
from typing import Callable

from src.window.events.editor_tab.parameters.editor_template_parameter import EditorTemplateParameter
from src.window.theme import Theme


class StringParameter(EditorTemplateParameter):
    def __init__(self, key: str, label: str, default: str, helpText: str | None = None, width: int = 34) -> None:
        super().__init__(key=key, label=label, helpText=helpText)
        self._default = str(default)
        self._width = int(width)
        self._var: tk.StringVar | None = None

    def Build(self, parent: tk.Frame, onChanged: Callable[[], None]) -> None:
        palette = Theme.Palette
        row = self._BuildRowContainer(parent)

        tk.Label(row, text=self.label, bg=palette.surface, fg=palette.text, width=22, anchor="w").pack(side=tk.LEFT)

        self._var = tk.StringVar(value=self._default)
        entry = tk.Entry(row, textvariable=self._var, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT, width=self._width)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        entry.bind("<KeyRelease>", lambda event: onChanged())

    def GetValue(self) -> object:
        if self._var is None:
            return str(self._default)
        try:
            return str(self._var.get())
        except Exception:
            return str(self._default)
