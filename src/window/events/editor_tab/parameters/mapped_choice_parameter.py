from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Tuple

from src.window.events.editor_tab.parameters.editor_template_parameter import EditorTemplateParameter
from src.window.theme import Theme


class MappedChoiceParameter(EditorTemplateParameter):
    def __init__(
        self,
        key: str,
        label: str,
        options: List[Tuple[str, str]],
        defaultValue: str,
        helpText: str | None = None,
    ) -> None:
        super().__init__(key=key, label=label, helpText=helpText)

        self._displayToValue: Dict[str, str] = {}
        self._displayOptions: List[str] = []

        for display, value in options or []:
            displayText = str(display).strip()
            valueText = str(value).strip()
            if displayText == "" or valueText == "":
                continue
            if displayText in self._displayToValue:
                displayText = f"{displayText} ({valueText})"
            self._displayToValue[displayText] = valueText
            self._displayOptions.append(displayText)

        self._defaultValue = str(defaultValue).strip()
        self._defaultDisplay = self.__ResolveDisplayForValue(self._defaultValue)
        if self._defaultDisplay is None and self._displayOptions:
            self._defaultDisplay = self._displayOptions[0]

        self._var: tk.StringVar | None = None

    def __ResolveDisplayForValue(self, value: str) -> str | None:
        for display, mappedValue in self._displayToValue.items():
            if mappedValue == value:
                return display
        return None

    def Build(self, parent: tk.Frame, onChanged: Callable[[], None]) -> None:
        palette = Theme.Palette
        row = self._BuildRowContainer(parent)

        tk.Label(row, text=self.label, bg=palette.surface, fg=palette.text, width=22, anchor="w").pack(side=tk.LEFT)

        self._var = tk.StringVar(value=self._defaultDisplay or "")
        combo = ttk.Combobox(row, textvariable=self._var, values=self._displayOptions, state="readonly")
        combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        combo.bind("<<ComboboxSelected>>", lambda event: onChanged())

    def GetValue(self) -> object:
        if self._var is None:
            return self._defaultValue
        selection = str(self._var.get() or "")
        if selection in self._displayToValue:
            return str(self._displayToValue[selection])
        return self._defaultValue
