from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class EventsWindowState:
    def __init__(self) -> None:
        self.window: tk.Toplevel | None = None
        self.tabs: ttk.Notebook | None = None
        self.catalogTabFrame: tk.Frame | None = None
        self.randomTabFrame: tk.Frame | None = None
        self.editorTabFrame: tk.Frame | None = None
        self.statusVar: tk.StringVar | None = None
        self.reloadButton: tk.Button | None = None
        self.openButton: tk.Button | None = None

    def IsOpen(self) -> bool:
        window = self.window
        return window is not None and window.winfo_exists()

    def Lift(self) -> None:
        window = self.window
        if window is None:
            return
        try:
            window.lift()
        except Exception:
            return

    def Assign(
        self,
        window: tk.Toplevel,
        tabs: ttk.Notebook,
        catalogTabFrame: tk.Frame,
        randomTabFrame: tk.Frame,
        editorTabFrame: tk.Frame,
        statusVar: tk.StringVar,
        reloadButton: tk.Button,
        openButton: tk.Button,
    ) -> None:
        self.window = window
        self.tabs = tabs
        self.catalogTabFrame = catalogTabFrame
        self.randomTabFrame = randomTabFrame
        self.editorTabFrame = editorTabFrame
        self.statusVar = statusVar
        self.reloadButton = reloadButton
        self.openButton = openButton

    def Destroy(self) -> None:
        window = self.window
        if window is not None:
            try:
                if window.winfo_exists():
                    window.destroy()
            except Exception:
                pass

        self.window = None
        self.tabs = None
        self.catalogTabFrame = None
        self.randomTabFrame = None
        self.editorTabFrame = None
        self.statusVar = None
        self.reloadButton = None
        self.openButton = None
