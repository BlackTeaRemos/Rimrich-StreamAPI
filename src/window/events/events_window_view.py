from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Tuple

from src.core.localization.localizer import Localizer
from src.window.theme import Theme


class EventsWindowView:
    def Build(
        self,
        parent: tk.Tk,
        localizer: Localizer,
        onReloadRequested: Callable[[], None],
        onOpenFileRequested: Callable[[], None],
        onCloseRequested: Callable[[], None],
        buildProtectionLabel: Callable[[tk.Misc, str, str], tk.Widget],
    ) -> Tuple[tk.Toplevel, ttk.Notebook, tk.Frame, tk.Frame, tk.Frame, tk.StringVar, tk.Button, tk.Button]:
        window = tk.Toplevel(parent)
        window.title(localizer.Text("events.title"))
        window.geometry("860x620")
        Theme.Apply(window)
        window.transient(parent)
        window.resizable(True, True)

        palette = Theme.Palette

        header = tk.Frame(window, bg=palette.surface)
        header.pack(fill=tk.X, padx=10, pady=(10, 6))

        title = tk.Label(header, text=localizer.Text("events.title"), bg=palette.surface, fg=palette.text, font=("Segoe UI Semibold", 12))
        title.pack(side=tk.LEFT)

        protectionLabel = buildProtectionLabel(header, palette.surface, palette.textFaint)
        protectionLabel.pack(side=tk.LEFT, padx=(12, 0))

        reloadButton = tk.Button(
            header,
            text=localizer.Text("events.button.reload"),
            command=onReloadRequested,
            bg=palette.button,
            fg=palette.text,
            activebackground=palette.buttonHover,
            activeforeground=palette.text,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            width=8,
        )
        Theme.TryAddHover(reloadButton, palette.button, palette.buttonHover)
        reloadButton.pack(side=tk.RIGHT, padx=(6, 0))

        openButton = tk.Button(
            header,
            text=localizer.Text("events.button.openFile"),
            command=onOpenFileRequested,
            bg=palette.button,
            fg=palette.text,
            activebackground=palette.buttonHover,
            activeforeground=palette.text,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            width=10,
        )
        Theme.TryAddHover(openButton, palette.button, palette.buttonHover)
        openButton.pack(side=tk.RIGHT, padx=(6, 0))

        closeButton = tk.Button(
            header,
            text=localizer.Text("events.button.close"),
            command=onCloseRequested,
            bg=palette.button,
            fg=palette.text,
            activebackground=palette.buttonHover,
            activeforeground=palette.text,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            width=8,
        )
        Theme.TryAddHover(closeButton, palette.button, palette.buttonHover)
        closeButton.pack(side=tk.RIGHT)

        body = tk.Frame(window, bg=palette.surface)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        tabs = ttk.Notebook(body)
        tabs.pack(fill=tk.BOTH, expand=True)

        catalogTabFrame = tk.Frame(tabs, bg=palette.surface)
        randomTabFrame = tk.Frame(tabs, bg=palette.surface)
        editorTabFrame = tk.Frame(tabs, bg=palette.surface)
        tabs.add(catalogTabFrame, text=localizer.Text("events.tab.catalog"))
        tabs.add(randomTabFrame, text=localizer.Text("events.tab.random"))
        tabs.add(editorTabFrame, text=localizer.Text("events.tab.editor"))

        statusRow = tk.Frame(window, bg=palette.surface)
        statusRow.pack(fill=tk.X, padx=10, pady=(0, 10))

        statusVar = tk.StringVar(value="")
        statusLabel = tk.Label(statusRow, textvariable=statusVar, bg=palette.surface, fg=palette.textFaint, anchor="w")
        statusLabel.pack(side=tk.LEFT, fill=tk.X, expand=True)

        return window, tabs, catalogTabFrame, randomTabFrame, editorTabFrame, statusVar, reloadButton, openButton
