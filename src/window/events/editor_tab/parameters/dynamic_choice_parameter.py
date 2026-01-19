from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, List

from src.window.events.editor_tab.parameters.editor_template_parameter import EditorTemplateParameter
from src.window.theme import Theme
from src.window.busy_button_task import BusyButtonTask


class DynamicChoiceParameter(EditorTemplateParameter):
    def __init__(
        self,
        key: str,
        label: str,
        fetchOptions: Callable[[], List[str]],
        default: str,
        allowManual: bool = True,
        helpText: str | None = None,
    ) -> None:
        super().__init__(key=key, label=label, helpText=helpText)
        self._fetchOptions = fetchOptions
        self._default = str(default)
        self._allowManual = bool(allowManual)

        self._var: tk.StringVar | None = None
        self._combo: ttk.Combobox | None = None
        self._refreshTask: BusyButtonTask[List[str]] | None = None

    def Build(self, parent: tk.Frame, onChanged: Callable[[], None]) -> None:
        palette = Theme.Palette
        row = self._BuildRowContainer(parent)

        tk.Label(row, text=self.label, bg=palette.surface, fg=palette.text, width=22, anchor="w").pack(side=tk.LEFT)

        self._var = tk.StringVar(value=self._default)
        state = "normal" if self._allowManual else "readonly"
        self._combo = ttk.Combobox(row, textvariable=self._var, values=[], state=state)
        self._combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))
        self._combo.bind("<<ComboboxSelected>>", lambda event: onChanged())
        if self._allowManual:
            self._combo.bind("<KeyRelease>", lambda event: onChanged())

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
            onSuccess=lambda options: self.__ApplyOptions(options, onChanged, preserveValue=True),
            onError=lambda error: self.__ApplyOptions([], onChanged, preserveValue=True),
        )

        self.__RefreshAsync(onChanged, preserveValue=True)

    def __RefreshAsync(self, onChanged: Callable[[], None], preserveValue: bool = True) -> None:
        task = self._refreshTask
        if task is None:
            return
        task.Invoke()

    def __FetchOptions(self) -> List[str]:
        try:
            return [str(value) for value in (self._fetchOptions() or []) if str(value).strip()]
        except Exception:
            return []

    def __ApplyOptions(self, options: List[str], onChanged: Callable[[], None], preserveValue: bool = True) -> None:
        if self._combo is None or self._var is None:
            return

        current = str(self._var.get() or "")

        try:
            self._combo.configure(values=options)
        except Exception:
            pass

        if preserveValue and current.strip() != "":
            return

        if options:
            try:
                self._var.set(options[0])
            except Exception:
                pass
        else:
            try:
                self._var.set(self._default)
            except Exception:
                pass
        onChanged()

    def GetValue(self) -> object:
        if self._var is None:
            return str(self._default)
        try:
            return str(self._var.get()).strip()
        except Exception:
            return str(self._default)
