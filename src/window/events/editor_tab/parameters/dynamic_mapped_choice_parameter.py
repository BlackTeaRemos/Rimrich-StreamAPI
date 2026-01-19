from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Tuple

from src.window.events.editor_tab.parameters.editor_template_parameter import EditorTemplateParameter
from src.window.theme import Theme
from src.window.busy_button_task import BusyButtonTask


class DynamicMappedChoiceParameter(EditorTemplateParameter):
    def __init__(
        self,
        key: str,
        label: str,
        fetchOptions: Callable[[], List[Tuple[str, int]]],
        defaultValue: int,
        helpText: str | None = None,
    ) -> None:
        super().__init__(key=key, label=label, helpText=helpText)
        self._fetchOptions = fetchOptions
        self._defaultValue = int(defaultValue)

        self._displayToValue: Dict[str, int] = {}
        self._var: tk.StringVar | None = None
        self._combo: ttk.Combobox | None = None
        self._refreshTask: BusyButtonTask[List[Tuple[str, int]]] | None = None

    def Build(self, parent: tk.Frame, onChanged: Callable[[], None]) -> None:
        palette = Theme.Palette
        row = self._BuildRowContainer(parent)

        tk.Label(row, text=self.label, bg=palette.surface, fg=palette.text, width=22, anchor="w").pack(side=tk.LEFT)

        self._var = tk.StringVar(value=str(self._defaultValue))
        self._combo = ttk.Combobox(row, textvariable=self._var, values=[], state="readonly")
        self._combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))
        self._combo.bind("<<ComboboxSelected>>", lambda event: onChanged())

        refreshButton = tk.Button(
            row,
            text="↻",
            command=lambda: self.__RefreshAsync(onChanged),
            bg=palette.button,
            fg=palette.text,
            activebackground=palette.buttonHover,
            activeforeground=palette.text,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            width=2,
        )
        Theme.TryAddHover(refreshButton, palette.button, palette.buttonHover)
        refreshButton.pack(side=tk.RIGHT)

        self._refreshTask = BusyButtonTask(
            refreshButton,
            work=self.__FetchOptions,
            onSuccess=lambda options: self.__ApplyOptions(options, onChanged, preserveSelection=True),
            onError=lambda error: self.__ApplyOptions([], onChanged, preserveSelection=True),
        )

        self.__RefreshAsync(onChanged, preserveSelection=True)

    def __RefreshAsync(self, onChanged: Callable[[], None], preserveSelection: bool = True) -> None:
        task = self._refreshTask
        if task is None:
            return
        task.Invoke()

    def __FetchOptions(self) -> List[Tuple[str, int]]:
        try:
            return list(self._fetchOptions() or [])
        except Exception:
            return []

    def __ApplyOptions(self, options: List[Tuple[str, int]], onChanged: Callable[[], None], preserveSelection: bool = True) -> None:
        if self._combo is None or self._var is None:
            return

        current = str(self._var.get() or "")

        self._displayToValue = {}
        displayValues: List[str] = []
        for display, value in options:
            displayText = str(display)
            displayValues.append(displayText)
            self._displayToValue[displayText] = int(value)

        try:
            self._combo.configure(values=displayValues)
        except Exception:
            pass

        if preserveSelection and current in self._displayToValue:
            return

        if displayValues:
            try:
                self._var.set(displayValues[0])
            except Exception:
                pass
        else:
            try:
                self._var.set(str(self._defaultValue))
            except Exception:
                pass
        onChanged()

    def GetValue(self) -> object:
        if self._var is None:
            return int(self._defaultValue)
        display = str(self._var.get() or "")
        if display in self._displayToValue:
            return int(self._displayToValue[display])
        try:
            return int(display)
        except Exception:
            return int(self._defaultValue)
