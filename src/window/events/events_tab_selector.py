from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class EventsTabSelector:
    def Select(
        self,
        tabs: ttk.Notebook | None,
        catalogTabFrame: tk.Frame | None,
        randomTabFrame: tk.Frame | None,
        editorTabFrame: tk.Frame | None,
        initialTab: str | None,
    ) -> None:
        if tabs is None:
            return
        if initialTab is None:
            return

        key = str(initialTab).strip().lower()

        if key in ["random", "randoms", "poll", "voting"]:
            try:
                tabs.select(randomTabFrame)
            except Exception:
                return

        if key in ["editor", "edit", "builder", "templates"]:
            try:
                tabs.select(editorTabFrame)
            except Exception:
                return

        if key in ["catalog", "events", "list"]:
            try:
                tabs.select(catalogTabFrame)
            except Exception:
                return
