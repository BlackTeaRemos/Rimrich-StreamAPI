from __future__ import annotations

import tkinter as tk
from typing import Callable

from src.window.events.editor_tab.parameters.editor_template_parameter import EditorTemplateParameter
from src.window.theme import Theme


class FloatSliderParameter(EditorTemplateParameter):
    def __init__(
        self,
        key: str,
        label: str,
        minimum: float,
        maximum: float,
        default: float,
        resolution: float = 0.1,
        helpText: str | None = None,
    ) -> None:
        super().__init__(key=key, label=label, helpText=helpText)
        self._minimum = float(minimum)
        self._maximum = float(maximum)
        self._default = float(default)
        self._resolution = float(resolution)
        self._var: tk.DoubleVar | None = None
        self._valueLabel: tk.Label | None = None

    def Build(self, parent: tk.Frame, onChanged: Callable[[], None]) -> None:
        palette = Theme.Palette
        row = self._BuildRowContainer(parent)

        label = tk.Label(row, text=self.label, bg=palette.surface, fg=palette.text, width=22, anchor="w")
        label.pack(side=tk.LEFT)

        self._var = tk.DoubleVar(value=self._default)

        def onScaleChanged(value: str) -> None:
            if self._valueLabel is not None:
                try:
                    self._valueLabel.configure(text=f"{float(value):.2f}")
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
            resolution=self._resolution,
            bg=palette.surface,
            fg=palette.textMuted,
            troughcolor=palette.button,
            activebackground=palette.accent,
            highlightthickness=0,
            command=onScaleChanged,
        )
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))

        self._valueLabel = tk.Label(row, text=f"{self._default:.2f}", bg=palette.surface, fg=palette.textFaint, width=8, anchor="e")
        self._valueLabel.pack(side=tk.RIGHT)

        Theme.TryAddHover(label, palette.surface, palette.surfaceAlt)

    def GetValue(self) -> object:
        if self._var is None:
            return float(self._default)
        try:
            return float(self._var.get())
        except Exception:
            return float(self._default)
