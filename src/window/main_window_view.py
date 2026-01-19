from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Tuple

from src.core.localization.localizer import Localizer
from src.window.theme import Theme


class MainWindowView:
    def Build(
        self,
        root: tk.Tk,
        localizer: Localizer,
        onExitRequested: Callable[[], None],
        onShowOverlayRequested: Callable[[], None],
        onConnectRequested: Callable[[ttk.Button], None],
        onDisconnectRequested: Callable[[ttk.Button], None],
        onOpenSettingsRequested: Callable[[], None],
        onOpenChatRequested: Callable[[], None],
        onOpenEventsRequested: Callable[[], None],
    ) -> Tuple[ttk.Notebook, tk.StringVar, tk.StringVar]:
        palette = Theme.Palette

        header = tk.Frame(root, bg=palette.surface)
        header.pack(fill=tk.X, padx=10, pady=(10, 6))

        title = tk.Label(
            header,
            text=localizer.Text("main.header.title"),
            bg=palette.surface,
            fg=palette.text,
            font=("Segoe UI Semibold", 12),
        )
        title.pack(side=tk.LEFT)

        closeButton = tk.Button(
            header,
            text=localizer.Text("main.button.exit"),
            command=onExitRequested,
            bg=palette.button,
            fg=palette.text,
            activebackground=palette.buttonHover,
            activeforeground=palette.text,
            relief=tk.FLAT,
            borderwidth=0,
            width=6,
            highlightthickness=0,
        )
        Theme.TryAddHover(closeButton, palette.button, palette.buttonHover)
        closeButton.pack(side=tk.RIGHT)

        body = tk.Frame(root, bg=palette.surface)
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        tabs = ttk.Notebook(body)
        tabs.pack(fill=tk.BOTH, expand=True)

        dashboardTab = tk.Frame(tabs, bg=palette.surface)
        twitchTab = tk.Frame(tabs, bg=palette.surface)
        windowsTab = tk.Frame(tabs, bg=palette.surface)
        tabs.add(dashboardTab, text=localizer.Text("main.tab.dashboard"))
        tabs.add(twitchTab, text=localizer.Text("main.tab.twitch"))
        tabs.add(windowsTab, text=localizer.Text("main.tab.windows"))

        # Dashboard
        primary = ttk.Button(
            dashboardTab,
            text=localizer.Text("main.dashboard.showOverlay"),
            command=onShowOverlayRequested,
            style="Accent.TButton",
        )
        primary.pack(fill=tk.X, padx=10, pady=(12, 10), ipady=4)

        twitchStatusVar = tk.StringVar(value=localizer.Text("main.dashboard.twitchStatus.unknown"))
        twitchStatus = tk.Label(dashboardTab, textvariable=twitchStatusVar, bg=palette.surface, fg=palette.textMuted, anchor="w")
        twitchStatus.pack(fill=tk.X, padx=10, pady=(0, 8))

        actions = tk.Frame(dashboardTab, bg=palette.surface)
        actions.pack(fill=tk.X, padx=10, pady=(0, 10))

        connectButton = ttk.Button(actions, text=localizer.Text("main.dashboard.connect"), style="Accent.TButton")
        connectButton.pack(side=tk.LEFT)
        connectButton.configure(command=lambda: onConnectRequested(connectButton))

        disconnectButton = ttk.Button(actions, text=localizer.Text("main.dashboard.disconnect"), style="Neutral.TButton")
        disconnectButton.pack(side=tk.LEFT, padx=(8, 0))
        disconnectButton.configure(command=lambda: onDisconnectRequested(disconnectButton))

        settingsButton = ttk.Button(actions, text=localizer.Text("main.dashboard.settings"), command=onOpenSettingsRequested, style="Neutral.TButton")
        settingsButton.pack(side=tk.RIGHT)

        # Twitch tab
        twitchBody = tk.Frame(twitchTab, bg=palette.surface)
        twitchBody.pack(fill=tk.BOTH, expand=True, padx=10, pady=12)

        twitchTitle = tk.Label(
            twitchBody,
            text=localizer.Text("main.twitch.title"),
            bg=palette.surface,
            fg=palette.text,
            font=("Segoe UI Semibold", 12),
        )
        twitchTitle.pack(anchor="w")

        twitchHelp = tk.Label(
            twitchBody,
            text=localizer.Text("main.twitch.help"),
            bg=palette.surface,
            fg=palette.textFaint,
            justify=tk.LEFT,
            wraplength=460,
        )
        twitchHelp.pack(anchor="w", pady=(4, 10))

        statusRow = tk.Frame(twitchBody, bg=palette.surface)
        statusRow.pack(fill=tk.X, pady=(0, 12))

        tk.Label(statusRow, text=localizer.Text("main.twitch.statusLabel"), bg=palette.surface, fg=palette.textMuted).pack(side=tk.LEFT)
        statusValue = tk.Label(statusRow, textvariable=twitchStatusVar, bg=palette.surface, fg=palette.text)
        statusValue.pack(side=tk.LEFT, padx=(8, 0))

        twitchButtons = tk.Frame(twitchBody, bg=palette.surface)
        twitchButtons.pack(fill=tk.X)

        twitchConnectButton = ttk.Button(twitchButtons, text=localizer.Text("main.dashboard.connect"), style="Accent.TButton")
        twitchConnectButton.pack(side=tk.LEFT)
        twitchConnectButton.configure(command=lambda: onConnectRequested(twitchConnectButton))

        twitchDisconnectButton = ttk.Button(twitchButtons, text=localizer.Text("main.dashboard.disconnect"), style="Neutral.TButton")
        twitchDisconnectButton.pack(side=tk.LEFT, padx=(8, 0))
        twitchDisconnectButton.configure(command=lambda: onDisconnectRequested(twitchDisconnectButton))

        ttk.Button(twitchButtons, text=localizer.Text("main.twitch.openChat"), command=onOpenChatRequested, style="Neutral.TButton").pack(side=tk.RIGHT)

        # Windows tab
        windowsBody = tk.Frame(windowsTab, bg=palette.surface)
        windowsBody.pack(fill=tk.BOTH, expand=True, padx=10, pady=12)

        ttk.Button(windowsBody, text=localizer.Text("main.windows.chat"), command=onOpenChatRequested, style="Neutral.TButton").pack(fill=tk.X, pady=(0, 10), ipady=3)
        ttk.Button(windowsBody, text=localizer.Text("main.windows.events"), command=onOpenEventsRequested, style="Neutral.TButton").pack(fill=tk.X, pady=(0, 10), ipady=3)
        ttk.Button(windowsBody, text=localizer.Text("main.windows.settings"), command=onOpenSettingsRequested, style="Neutral.TButton").pack(fill=tk.X, ipady=3)

        # Status bar
        statusVar = tk.StringVar(value="")
        statusBar = tk.Label(root, textvariable=statusVar, bg=palette.surface, fg=palette.textFaint, anchor="w")
        statusBar.pack(fill=tk.X, padx=10, pady=(0, 10))

        return tabs, twitchStatusVar, statusVar
