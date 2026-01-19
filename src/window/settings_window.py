import tkinter as tk
from tkinter import ttk
from typing import Optional

from src.core.settings.settings_service import SettingsService
from src.core.localization.localizer_provider import LocalizerProvider
from src.window.busy_button_task import BusyButtonTask
from src.window.theme import Theme


class SettingsWindow:
    """Render a simple settings dialog.

    Args:
        service (SettingsService): settings manager.
        localizerProvider (LocalizerProvider | None): optional localizer provider.
    """

    def __init__(self, service: SettingsService, localizerProvider: LocalizerProvider | None = None) -> None:
        self.service = service  # settings manager
        self._localizerProvider = localizerProvider or LocalizerProvider(service)
        self._localizer = self._localizerProvider.Get()
        self._window: Optional[tk.Toplevel] = None  # dialog window
        self._borderlessVar: Optional[tk.BooleanVar] = None  # borderless toggle var
        self._tokenVar: Optional[tk.StringVar] = None  # twitch token value
        self._showTokenVar: Optional[tk.BooleanVar] = None
        self._nickVar: Optional[tk.StringVar] = None  # twitch nick value
        self._channelVar: Optional[tk.StringVar] = None  # twitch channel value
        self._chromaVar: Optional[tk.BooleanVar] = None  # chroma toggle
        self._chromaCountVar: Optional[tk.IntVar] = None  # chroma voters count
        self._rimApiHostVar: Optional[tk.StringVar] = None  # rim api host
        self._rimApiPortVar: Optional[tk.IntVar] = None  # rim api port
        self._uiLanguageVar: Optional[tk.StringVar] = None

    def Show(self, parent: tk.Tk) -> None:
        """Open the settings dialog.

        Args:
            parent (tk.Tk): owner window.

        Returns:
            None
        """

        if self._window is not None and self._window.winfo_exists():
            self._window.lift()
            return

        self._localizer = self._localizerProvider.Get()

        self._window = tk.Toplevel(parent)
        self._window.title(self._localizer.Text("settings.title"))
        self._window.geometry("360x360")
        Theme.Apply(self._window)
        self._window.transient(parent)
        self._window.resizable(True, True)
        settings = self.service.Get()
        defaultChannel = settings.twitchChannel if settings.twitchChannel else "mychannel"
        defaultNick = settings.twitchNick if settings.twitchNick else "mybot"
        defaultToken = settings.twitchToken if settings.twitchToken else "oauth:yourtoken"
        defaultChromaEnabled = settings.chromaEnabled
        defaultChromaCount = settings.chromaVoterCount if settings.chromaVoterCount else 0
        defaultRimApiHost = getattr(settings, "rimApiHost", "localhost") or "localhost"
        defaultRimApiPort = settings.rimApiPort if settings.rimApiPort else 0
        defaultUiLanguage = str(getattr(settings, "uiLanguage", "en") or "en")
        self._borderlessVar = tk.BooleanVar(value=settings.borderless)
        self._tokenVar = tk.StringVar(value=defaultToken)
        self._showTokenVar = tk.BooleanVar(value=False)
        self._nickVar = tk.StringVar(value=defaultNick)
        self._channelVar = tk.StringVar(value=defaultChannel)
        self._chromaVar = tk.BooleanVar(value=defaultChromaEnabled)
        self._chromaCountVar = tk.IntVar(value=defaultChromaCount)
        self._rimApiHostVar = tk.StringVar(value=defaultRimApiHost)
        self._rimApiPortVar = tk.IntVar(value=defaultRimApiPort)
        self._uiLanguageVar = tk.StringVar(value=defaultUiLanguage)
        self.__BuildContents()

    def __BuildContents(self) -> None:
        """Construct the dialog controls and wire up widgets.

        Returns:
            None
        """

        root = self._window
        if root is None:
            return
        palette = Theme.Palette
        outer = tk.Frame(root, bg="#1e1e1e")
        outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        tabs = ttk.Notebook(outer)
        tabs.pack(fill=tk.BOTH, expand=True)

        twitchTab = tk.Frame(tabs, bg=palette.surface)
        overlayTab = tk.Frame(tabs, bg=palette.surface)
        rimworldTab = tk.Frame(tabs, bg=palette.surface)
        tabs.add(twitchTab, text=self._localizer.Text("settings.tab.twitch"))
        tabs.add(overlayTab, text=self._localizer.Text("settings.tab.overlay"))
        tabs.add(rimworldTab, text=self._localizer.Text("settings.tab.rimworld"))

        # Twitch
        channelLabel = tk.Label(twitchTab, text=self._localizer.Text("settings.twitch.channel"), bg=palette.surface, fg=palette.text, font=("Segoe UI", 10))
        channelLabel.pack(anchor="w", pady=(10, 0), padx=6)
        channelEntry = tk.Entry(twitchTab, textvariable=self._channelVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
        channelEntry.pack(fill=tk.X, padx=6, pady=(0, 10))

        nickLabel = tk.Label(twitchTab, text=self._localizer.Text("settings.twitch.botUsername"), bg=palette.surface, fg=palette.text, font=("Segoe UI", 10))
        nickLabel.pack(anchor="w", padx=6)
        nickEntry = tk.Entry(twitchTab, textvariable=self._nickVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
        nickEntry.pack(fill=tk.X, padx=6, pady=(0, 10))

        tokenLabel = tk.Label(twitchTab, text=self._localizer.Text("settings.twitch.oauthToken"), bg=palette.surface, fg=palette.text, font=("Segoe UI", 10))
        tokenLabel.pack(anchor="w", padx=6)
        tokenEntry = tk.Entry(twitchTab, textvariable=self._tokenVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT, show="*")
        tokenEntry.pack(fill=tk.X, padx=6, pady=(0, 6))

        showToken = tk.Checkbutton(
            twitchTab,
            text=self._localizer.Text("settings.twitch.showToken"),
            variable=self._showTokenVar,
            bg=palette.surface,
            fg=palette.text,
            activebackground=palette.surface,
            selectcolor=palette.surface,
            highlightthickness=0,
            command=lambda: tokenEntry.config(show="" if bool(self._showTokenVar.get()) else "*"),
        )
        showToken.pack(anchor="w", padx=6, pady=(0, 10))

        # Overlay
        toggle = tk.Checkbutton(
            overlayTab,
            text=self._localizer.Text("settings.overlay.borderless"),
            variable=self._borderlessVar,
            bg=palette.surface,
            fg=palette.text,
            activebackground=palette.surface,
            selectcolor=palette.surface,
            highlightthickness=0,
        )
        toggle.pack(anchor="w", padx=6, pady=(10, 10))

        chromaToggle = tk.Checkbutton(
            overlayTab,
            text=self._localizer.Text("settings.overlay.chroma"),
            variable=self._chromaVar,
            bg=palette.surface,
            fg=palette.text,
            activebackground=palette.surface,
            selectcolor=palette.surface,
            highlightthickness=0,
        )
        chromaToggle.pack(anchor="w", padx=6, pady=(0, 8))

        chromaCountLabel = tk.Label(overlayTab, text=self._localizer.Text("settings.overlay.chromaCount"), bg=palette.surface, fg=palette.text, font=("Segoe UI", 10))
        chromaCountLabel.pack(anchor="w", padx=6)
        chromaCountSpin = tk.Spinbox(overlayTab, from_=0, to=3, textvariable=self._chromaCountVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
        chromaCountSpin.pack(fill=tk.X, padx=6, pady=(0, 10))

        uiLanguageLabel = tk.Label(overlayTab, text=self._localizer.Text("settings.overlay.uiLanguage"), bg=palette.surface, fg=palette.text, font=("Segoe UI", 10))
        uiLanguageLabel.pack(anchor="w", padx=6)
        uiLanguageEntry = tk.Entry(overlayTab, textvariable=self._uiLanguageVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
        uiLanguageEntry.pack(fill=tk.X, padx=6, pady=(0, 10))

        # RimWorld
        rimApiHostLabel = tk.Label(rimworldTab, text=self._localizer.Text("settings.rimworld.host"), bg=palette.surface, fg=palette.text, font=("Segoe UI", 10))
        rimApiHostLabel.pack(anchor="w", padx=6, pady=(10, 0))
        rimApiHostEntry = tk.Entry(rimworldTab, textvariable=self._rimApiHostVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
        rimApiHostEntry.pack(fill=tk.X, padx=6, pady=(0, 10))

        rimApiLabel = tk.Label(rimworldTab, text=self._localizer.Text("settings.rimworld.port"), bg=palette.surface, fg=palette.text, font=("Segoe UI", 10))
        rimApiLabel.pack(anchor="w", padx=6)
        rimApiSpin = tk.Spinbox(rimworldTab, from_=0, to=65535, textvariable=self._rimApiPortVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
        rimApiSpin.pack(fill=tk.X, padx=6, pady=(0, 10))

        actions = tk.Frame(outer, bg=palette.surface)
        actions.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        cancelButton = ttk.Button(actions, text=self._localizer.Text("settings.button.cancel"), command=self.__HandleCancel, style="Neutral.TButton")
        cancelButton.pack(side=tk.RIGHT)

        saveButton = ttk.Button(actions, text=self._localizer.Text("settings.button.save"), command=self.__HandleSave, style="Accent.TButton")
        saveButton.pack(side=tk.RIGHT, padx=(0, 8))
        try:
            saveButton.configure(command=lambda: self.__HandleSaveFromButton(saveButton))
        except Exception:
            pass

    def __HandleCancel(self) -> None:
        if self._window is not None:
            try:
                self._window.destroy()
            except Exception:
                pass
            self._window = None

    def __HandleSave(self) -> None:
        """Persist settings and close the dialog.

        Returns:
            None
        """

        values = self.__CollectInputValues()
        if values is None:
            return
        self.__PersistSettings(*values)
        self.__CloseWindow()

    def __HandleSaveFromButton(self, button: ttk.Button) -> None:
        values = self.__CollectInputValues()
        if values is None:
            return

        def persist() -> None:
            self.__PersistSettings(*values)

        BusyButtonTask(
            button,
            work=persist,
            onSuccess=lambda _: self.__CloseWindow(),
            onError=lambda _: self.__CloseWindow(),
            busyText="Saving...",
        ).Invoke()

    def __CollectInputValues(self) -> tuple[bool, str, str, str, bool, int, str, int, str] | None:
        if (
            self._borderlessVar is None
            or self._tokenVar is None
            or self._nickVar is None
            or self._channelVar is None
            or self._chromaVar is None
            or self._chromaCountVar is None
            or self._rimApiHostVar is None
            or self._rimApiPortVar is None
            or self._uiLanguageVar is None
        ):
            return None

        try:
            borderless = bool(self._borderlessVar.get())
            token = str(self._tokenVar.get())
            nick = str(self._nickVar.get())
            channel = str(self._channelVar.get())
            chromaEnabled = bool(self._chromaVar.get())
            chromaCount = int(self._chromaCountVar.get())
            rimApiHost = str(self._rimApiHostVar.get())
            rimApiPort = int(self._rimApiPortVar.get())
            uiLanguage = str(self._uiLanguageVar.get())
        except Exception:
            return None

        return (borderless, token, nick, channel, chromaEnabled, chromaCount, rimApiHost, rimApiPort, uiLanguage)

    def __PersistSettings(
        self,
        borderless: bool,
        token: str,
        nick: str,
        channel: str,
        chromaEnabled: bool,
        chromaCount: int,
        rimApiHost: str,
        rimApiPort: int,
        uiLanguage: str,
    ) -> None:
        self.service.UpdateBorderless(borderless)
        self.service.UpdateTwitch(token, nick, channel)
        self.service.UpdateChroma(chromaEnabled, chromaCount)
        self.service.UpdateRimApiEndpoint(rimApiHost, rimApiPort)
        self.service.UpdateUiLanguage(uiLanguage)

    def __CloseWindow(self) -> None:
        if self._window is not None:
            try:
                self._window.destroy()
            except Exception:
                pass
            self._window = None
