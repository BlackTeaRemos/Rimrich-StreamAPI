from __future__ import annotations

import tkinter as tk
from typing import Callable

from src.window.events.editor_tab.parameters.editor_template_parameter import EditorTemplateParameter
from src.window.theme import Theme


class BoolParameter(EditorTemplateParameter):
    def __init__(self, key: str, label: str, default: bool, helpText: str | None = None) -> None:
        super().__init__(key=key, label=label, helpText=helpText)
        self._default = bool(default)
        self._var: tk.BooleanVar | None = None

    def Build(self, parent: tk.Frame, onChanged: Callable[[], None]) -> None:
        palette = Theme.Palette
        row = self._BuildRowContainer(parent)

        self._var = tk.BooleanVar(value=self._default)
        checkbox = tk.Checkbutton(
            row,
            text=self.label,
            variable=self._var,
            command=onChanged,
            bg=palette.surface,
            fg=palette.text,
            activebackground=palette.surface,
            activeforeground=palette.text,
            selectcolor=palette.button,
            highlightthickness=0,
        )
        checkbox.pack(side=tk.LEFT, anchor="w")

    def GetValue(self) -> object:
        if self._var is None:
            return bool(self._default)
        try:
            return bool(self._var.get())
        except Exception:
            return bool(self._default)
