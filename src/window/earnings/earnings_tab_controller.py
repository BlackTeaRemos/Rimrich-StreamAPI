from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from src.core.localization.localizer import Localizer
from src.purchases.interfaces.silver_earning_service_interface import SilverEarningServiceInterface
from src.purchases.models.silver_earning_configuration import SilverEarningConfiguration
from src.window.theme import Theme


class EarningsTabController:
    def __init__(self, silverEarningService: SilverEarningServiceInterface, localizer: Localizer) -> None:
        self._silverEarningService = silverEarningService
        self._localizer = localizer
        self._chatMessageVar: tk.IntVar | None = None
        self._pollVoteVar: tk.IntVar | None = None
        self._cooldownSecondsVar: tk.DoubleVar | None = None
        self._statusVar: tk.StringVar | None = None

    def Build(self, parent: tk.Frame) -> None:
        palette = Theme.Palette

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        header = tk.Frame(parent, bg=palette.surface)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(12, 6))
        header.columnconfigure(1, weight=1)

        titleLabel = tk.Label(
            header,
            text=self._localizer.Text("earnings.title"),
            bg=palette.surface,
            fg=palette.text,
            font=("Segoe UI Semibold", 11),
        )
        titleLabel.grid(row=0, column=0, sticky="w")

        self._statusVar = tk.StringVar(value="")
        statusLabel = tk.Label(header, textvariable=self._statusVar, bg=palette.surface, fg=palette.textFaint, anchor="e")
        statusLabel.grid(row=0, column=1, sticky="e", padx=(8, 8))

        refreshButton = ttk.Button(
            header,
            text=self._localizer.Text("earnings.button.refresh"),
            command=self.Refresh,
            style="Neutral.TButton",
        )
        refreshButton.grid(row=0, column=2, sticky="e")

        applyButton = ttk.Button(
            header,
            text=self._localizer.Text("earnings.button.apply"),
            command=self.__HandleApply,
            style="Accent.TButton",
        )
        applyButton.grid(row=0, column=3, sticky="e", padx=(8, 0))

        body = tk.Frame(parent, bg=palette.surfaceDeep)
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        body.columnconfigure(1, weight=1)

        self._chatMessageVar = tk.IntVar(value=0)
        self._pollVoteVar = tk.IntVar(value=0)
        self._cooldownSecondsVar = tk.DoubleVar(value=0.0)

        self.__AddRow(
            body,
            rowIndex=0,
            labelText=self._localizer.Text("earnings.label.chat"),
            variable=self._chatMessageVar,
            isFloat=False,
        )
        self.__AddRow(
            body,
            rowIndex=1,
            labelText=self._localizer.Text("earnings.label.vote"),
            variable=self._pollVoteVar,
            isFloat=False,
        )
        self.__AddRow(
            body,
            rowIndex=2,
            labelText=self._localizer.Text("earnings.label.cooldown"),
            variable=self._cooldownSecondsVar,
            isFloat=True,
        )

        helpLabel = tk.Label(
            body,
            text=self._localizer.Text("earnings.help"),
            bg=palette.surfaceDeep,
            fg=palette.textMuted,
            justify=tk.LEFT,
            wraplength=420,
        )
        helpLabel.grid(row=3, column=0, columnspan=2, sticky="w", padx=6, pady=(8, 4))

        self.Refresh()

    def Refresh(self) -> None:
        configuration = self._silverEarningService.GetConfiguration()
        if self._chatMessageVar is not None:
            self._chatMessageVar.set(int(configuration.silverPerChatMessage))
        if self._pollVoteVar is not None:
            self._pollVoteVar.set(int(configuration.silverPerPollVote))
        if self._cooldownSecondsVar is not None:
            self._cooldownSecondsVar.set(float(configuration.chatRewardCooldownSeconds))
        self.__SetStatus("")

    def __AddRow(self, parent: tk.Frame, rowIndex: int, labelText: str, variable: tk.Variable, isFloat: bool) -> None:
        palette = Theme.Palette
        label = tk.Label(parent, text=labelText, bg=palette.surfaceDeep, fg=palette.text, font=("Segoe UI", 10))
        label.grid(row=rowIndex, column=0, sticky="w", padx=6, pady=(8, 4))

        if isFloat:
            entry = tk.Entry(parent, textvariable=variable, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
            entry.grid(row=rowIndex, column=1, sticky="ew", padx=6, pady=(8, 4))
        else:
            spinbox = tk.Spinbox(parent, from_=0, to=999999, textvariable=variable, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
            spinbox.grid(row=rowIndex, column=1, sticky="ew", padx=6, pady=(8, 4))

    def __HandleApply(self) -> None:
        if self._chatMessageVar is None or self._pollVoteVar is None or self._cooldownSecondsVar is None:
            return
        try:
            chatAmount = int(self._chatMessageVar.get())
            pollAmount = int(self._pollVoteVar.get())
            cooldownSeconds = float(self._cooldownSecondsVar.get())
        except Exception:
            self.__ShowValidationError(self._localizer.Text("earnings.error.invalid"))
            return

        if chatAmount < 0 or pollAmount < 0 or cooldownSeconds < 0:
            self.__ShowValidationError(self._localizer.Text("earnings.error.negative"))
            return

        configuration = SilverEarningConfiguration(
            silverPerChatMessage=chatAmount,
            silverPerPollVote=pollAmount,
            chatRewardCooldownSeconds=cooldownSeconds,
        )
        self._silverEarningService.UpdateConfiguration(configuration)
        self.__SetStatus(self._localizer.Text("earnings.status.saved"))

    def __ShowValidationError(self, message: str) -> None:
        try:
            messagebox.showerror(self._localizer.Text("earnings.error.title"), message)
        except Exception:
            pass
        self.__SetStatus(self._localizer.Text("earnings.status.error"))

    def __SetStatus(self, text: str) -> None:
        if self._statusVar is not None:
            self._statusVar.set(str(text or ""))
