from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Tuple

from src.purchases.interfaces.balance_service_interface import BalanceServiceInterface
from src.core.localization.localizer import Localizer
from src.window.theme import Theme


class BalancesTabController:
    def __init__(self, balanceService: BalanceServiceInterface, localizer: Localizer) -> None:
        self._balanceService = balanceService
        self._localizer = localizer
        self._tree: ttk.Treeview | None = None
        self._countLabel: tk.Label | None = None
        self._emptyLabel: tk.Label | None = None

    def Build(self, parent: tk.Frame) -> None:
        palette = Theme.Palette

        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        header = tk.Frame(parent, bg=palette.surface)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(12, 6))

        title = tk.Label(
            header,
            text=self._localizer.Text("balances.title"),
            bg=palette.surface,
            fg=palette.text,
            font=("Segoe UI Semibold", 11),
        )
        title.pack(side=tk.LEFT)

        self._countLabel = tk.Label(header, text="0", bg=palette.surface, fg=palette.textFaint)
        self._countLabel.pack(side=tk.RIGHT)

        refreshButton = ttk.Button(
            header,
            text=self._localizer.Text("balances.button.refresh"),
            command=self.Refresh,
            style="Neutral.TButton",
        )
        refreshButton.pack(side=tk.RIGHT, padx=(0, 8))

        body = tk.Frame(parent, bg=palette.surfaceDeep)
        body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        listFrame = tk.Frame(body, bg=palette.surfaceDeep)
        listFrame.grid(row=0, column=0, sticky="nsew")

        treeScrollbar = ttk.Scrollbar(listFrame, orient="vertical")
        treeScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("user", "balance")
        self._tree = ttk.Treeview(listFrame, columns=columns, show="headings", selectmode="browse")
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._tree.configure(yscrollcommand=treeScrollbar.set)
        treeScrollbar.config(command=self._tree.yview)

        self._tree.heading("user", text=self._localizer.Text("balances.column.user"))
        self._tree.heading("balance", text=self._localizer.Text("balances.column.balance"))

        self._tree.column("user", width=280, anchor="w", stretch=True)
        self._tree.column("balance", width=90, anchor="e", stretch=False)

        try:
            self._tree.tag_configure("even", background=palette.surfaceDeep)
            self._tree.tag_configure("odd", background=palette.surface)
        except Exception:
            pass

        self._emptyLabel = tk.Label(
            body,
            text=self._localizer.Text("balances.empty"),
            bg=palette.surfaceDeep,
            fg=palette.textMuted,
            anchor="center",
        )
        self._emptyLabel.grid(row=0, column=0, sticky="nsew")

        self.Refresh()

    def Refresh(self) -> None:
        balances = self._balanceService.GetAllBalances()
        rows = self._SortBalances(balances)

        tree = self._tree
        if tree is None:
            return

        for itemId in tree.get_children():
            tree.delete(itemId)

        for index, (username, balance) in enumerate(rows):
            tag = "even" if index % 2 == 0 else "odd"
            tree.insert("", tk.END, values=(username, balance), tags=(tag,))

        if self._countLabel is not None:
            self._countLabel.config(text=str(len(rows)))

        if self._emptyLabel is not None:
            if rows:
                self._emptyLabel.lower()
            else:
                self._emptyLabel.lift()

    def _SortBalances(self, balances: Dict[str, int]) -> List[Tuple[str, int]]:
        rows = [(str(username), int(balance)) for username, balance in balances.items()]
        return sorted(rows, key=lambda item: (-item[1], item[0].lower()))