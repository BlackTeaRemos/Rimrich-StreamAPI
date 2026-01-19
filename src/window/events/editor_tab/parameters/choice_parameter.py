from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, List

from src.window.events.editor_tab.parameters.editor_template_parameter import EditorTemplateParameter
from src.window.theme import Theme


class ChoiceParameter(EditorTemplateParameter):
    def __init__(self, key: str, label: str, options: List[str], default: str, helpText: str | None = None) -> None:
        super().__init__(key=key, label=label, helpText=helpText)
        self._options = [str(value) for value in (options or []) if str(value).strip()]
        self._default = str(default)
        if self._default not in self._options and self._options:
            self._default = self._options[0]
        self._var: tk.StringVar | None = None

    def Build(self, parent: tk.Frame, onChanged: Callable[[], None]) -> None:
        palette = Theme.Palette
        row = self._BuildRowContainer(parent)

        tk.Label(row, text=self.label, bg=palette.surface, fg=palette.text, width=22, anchor="w").pack(side=tk.LEFT)

        self._var = tk.StringVar(value=self._default)
        combo = ttk.Combobox(row, textvariable=self._var, values=self._options, state="readonly")
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        combo.bind("<<ComboboxSelected>>", lambda event: onChanged())

    def GetValue(self) -> object:
        if self._var is None:
            return str(self._default)
        try:
            return str(self._var.get())
        except Exception:
            return str(self._default)
