from __future__ import annotations

import tkinter as tk
from typing import Callable

from src.window.events.editor_tab.parameters.editor_template_parameter import EditorTemplateParameter
from src.window.theme import Theme


class IntSliderParameter(EditorTemplateParameter):
    def __init__(self, key: str, label: str, minimum: int, maximum: int, default: int, helpText: str | None = None) -> None:
        super().__init__(key=key, label=label, helpText=helpText)
        self._minimum = int(minimum)
        self._maximum = int(maximum)
        self._default = int(default)
        self._var: tk.IntVar | None = None
        self._valueLabel: tk.Label | None = None

    def Build(self, parent: tk.Frame, onChanged: Callable[[], None]) -> None:
        palette = Theme.Palette
        row = self._BuildRowContainer(parent)

        label = tk.Label(row, text=self.label, bg=palette.surface, fg=palette.text, width=22, anchor="w")
        label.pack(side=tk.LEFT)

        self._var = tk.IntVar(value=self._default)

        def onScaleChanged(value: str) -> None:
            if self._valueLabel is not None:
                try:
                    self._valueLabel.configure(text=str(int(float(value))))
                except Exception:
                    pass
            onChanged()

        scale = tk.Scale(
            row,
            from_=self._minimum,
            to=self._maximum,
            orient=tk.HORIZONTAL,
            variable=self._var,
            showvalue=False,
            resolution=1,
            bg=palette.surface,
            fg=palette.textMuted,
            troughcolor=palette.button,
            activebackground=palette.accent,
            highlightthickness=0,
            command=onScaleChanged,
        )
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))

        self._valueLabel = tk.Label(row, text=str(self._default), bg=palette.surface, fg=palette.textFaint, width=6, anchor="e")
        self._valueLabel.pack(side=tk.RIGHT)

        Theme.TryAddHover(label, palette.surface, palette.surfaceAlt)

    def GetValue(self) -> object:
        if self._var is None:
            return int(self._default)
        try:
            return int(self._var.get())
        except Exception:
            return int(self._default)
