

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import List, Tuple

from src.events.app_exit_event import AppExitEvent
from src.core.events.event_bus import EventBus
from src.events.show_overlay_event import ShowOverlayEvent
from src.core.settings.settings_service import SettingsService
from src.twitch.twitch_chat_service import TwitchChatService
from src.features.overlay.service import Service
from src.window.chat_window_service import ChatWindowService
from src.window.events_window_service import EventsWindowService
from src.window.settings_window import SettingsWindow
from src.window.ui_thread_scheduler import UiThreadScheduler
from src.window.busy_button_task import BusyButtonTask
from src.window.main_window_view import MainWindowView
from src.window.theme import Theme
from src.core.localization.localizer_provider import LocalizerProvider
from src.purchases.interfaces.balance_service_interface import BalanceServiceInterface
from src.window.balances.balances_tab_controller import BalancesTabController


class MainWindowService:
    """Create and control the primary application window.

    Args:
        eventBus (EventBus): shared event bus.
        overlayService (Service): overlay controller.
        settingsWindow (SettingsWindow): settings dialog.
        settingsService (SettingsService): settings manager.
        twitchService (TwitchChatService): twitch chat manager.
        chatWindow (ChatWindowService): chat log window.
        eventsWindow (EventsWindowService): events window.
        balanceService (BalanceServiceInterface): balance service provider.
        uiScheduler (UiThreadScheduler | None): optional UI thread scheduler.
        localizerProvider (LocalizerProvider | None): optional localizer provider.
    """

    def __init__(
        self,
        eventBus: EventBus,
        overlayService: Service,
        settingsWindow: SettingsWindow,
        settingsService: SettingsService,
        twitchService: TwitchChatService,
        chatWindow: ChatWindowService,
        eventsWindow: EventsWindowService,
        balanceService: BalanceServiceInterface,
        uiScheduler: UiThreadScheduler | None = None,
        localizerProvider: LocalizerProvider | None = None,
    ) -> None:
        self.eventBus = eventBus  # shared event bus
        self.overlayService = overlayService  # overlay controller
        self.settingsWindow = settingsWindow  # settings dialog
        self.settingsService = settingsService  # settings manager
        self.twitchService = twitchService  # twitch chat manager
        self.chatWindow = chatWindow  # chat log window
        self.eventsWindow = eventsWindow  # events window
        self._balanceService = balanceService
        self._uiScheduler = uiScheduler
        self._localizerProvider = localizerProvider or LocalizerProvider(settingsService)
        self._localizer = self._localizerProvider.Get()
        self._view = MainWindowView()
        self._root: tk.Tk | None = None  # main window root
        self._borderlessVar: tk.BooleanVar | None = None  # toggle for borderless overlay
        self._twitchStatusVar: tk.StringVar | None = None
        self._statusVar: tk.StringVar | None = None
        self._tabs: ttk.Notebook | None = None
        self._balancesTabFrame: tk.Frame | None = None
        self._balancesTabController: BalancesTabController | None = None

    def ShowWindow(self) -> None:
        """Build and show the main window, then enter its event loop.

        Returns:
            None
        """

        if self._root is not None:
            return

        # Resolve localizer at window creation time so changed settings take effect.
        self._localizer = self._localizerProvider.Get()

        self._root = tk.Tk()
        self._root.title(self._localizer.Text("main.title"))
        self._root.geometry("520x420")
        Theme.Apply(self._root)
        self._root.protocol("WM_DELETE_WINDOW", lambda: self.eventBus.Publish(AppExitEvent()))

        if self._uiScheduler is not None:
            self._uiScheduler.Start(self._root)

        self.overlayService.AttachParent(self._root)
        self.__ConfigureContents()
        self._root.mainloop()

    def CloseWindow(self) -> None:
        """Destroy the main window if it exists and stop the UI scheduler.

        Returns:
            None
        """

        if self._root is None:
            return
        if self._uiScheduler is not None:
            try:
                self._uiScheduler.Stop()
            except Exception:
                pass
        try:
            self._root.destroy()
        except Exception:
            pass
        self._root = None

    def __ConfigureContents(self) -> None:
        """Build header and controls for the main window and initialize tabs.

        Returns:
            None
        """

        root = self._root
        if root is None:
            return

        tabs, twitchStatusVar, statusVar = self._view.Build(
            root,
            localizer=self._localizer,
            onExitRequested=lambda: self.eventBus.Publish(AppExitEvent()),
            onShowOverlayRequested=self.__HandleShowOverlay,
            onConnectRequested=self.__HandleConnectFromButton,
            onDisconnectRequested=self.__HandleDisconnectFromButton,
            onOpenSettingsRequested=self.__HandleOpenSettings,
            onOpenChatRequested=self.__HandleOpenChat,
            onOpenEventsRequested=self.__HandleOpenEvents,
        )

        self._tabs = tabs
        self._twitchStatusVar = twitchStatusVar
        self._statusVar = statusVar

        self.__AddBalancesTab()
        self.__BindTabRefresh()

        # Initialize status from current settings.
        settings = self.settingsService.Get()
        if settings.twitchChannel:
            self.SetTwitchStatus("idle", self._localizer.Text("main.twitch.configured", channel=settings.twitchChannel))
        else:
            self.SetTwitchStatus("missing_config", self._localizer.Text("main.twitch.missingConfig"))

    def __AddBalancesTab(self) -> None:
        tabs = self._tabs
        if tabs is None:
            return

        palette = Theme.Palette
        balancesTabFrame = tk.Frame(tabs, bg=palette.surface)
        tabs.add(balancesTabFrame, text=self._localizer.Text("main.tab.balances"))
        self._balancesTabFrame = balancesTabFrame
        self._balancesTabController = BalancesTabController(self._balanceService, self._localizer)
        self._balancesTabController.Build(balancesTabFrame)

    def __BindTabRefresh(self) -> None:
        tabs = self._tabs
        if tabs is None:
            return
        tabs.bind("<<NotebookTabChanged>>", lambda event: self.__RefreshBalancesIfSelected())

    def __RefreshBalancesIfSelected(self) -> None:
        tabs = self._tabs
        balancesTabFrame = self._balancesTabFrame
        controller = self._balancesTabController
        if tabs is None or balancesTabFrame is None or controller is None:
            return
        try:
            if tabs.select() == str(balancesTabFrame):
                controller.Refresh()
        except Exception:
            return

    def __HandleShowOverlay(self) -> None:
        """Publish a request to display the overlay with sample votes for testing.

        Returns:
            None
        """

        sampleVotes: List[Tuple[str, int]] = [
            ("Option A", 12),
            ("Option B", 9),
            ("Option C", 5),
            ("Option D", 4),
            ("Option E", 2),
        ]
        self.eventBus.Publish(ShowOverlayEvent(sampleVotes))

    def __HandleOpenSettings(self) -> None:
        """Open the settings dialog when requested from the UI.

        Returns:
            None
        """

        if self._root is None:
            return
        self.settingsWindow.Show(self._root)

    def __HandleOpenChat(self) -> None:
        """Open the chat log window when requested from the UI.

        Returns:
            None
        """

        if self._root is None:
            return
        self.chatWindow.ShowWindow(self._root)

    def __HandleOpenEvents(self) -> None:
        """Open the events window when requested from the UI.

        Returns:
            None
        """

        if self._root is None:
            return
        self.eventsWindow.ShowWindow(self._root)

    def __HandleTestConnect(self) -> None:
        """Trigger a reconnect attempt to the Twitch chat listener for testing.

        Returns:
            None
        """

        self.__HandleConnect()

    def __HandleConnect(self) -> None:
        try:
            self.twitchService.Start()
            self.__SetStatus(self._localizer.Text("main.status.connectRequested"))
        except Exception as error:
            try:
                messagebox.showerror(self._localizer.Text("main.dialog.twitch.title"), str(error))
            except Exception:
                pass

    def __HandleDisconnect(self) -> None:
        try:
            self.twitchService.Stop()
            self.__SetStatus(self._localizer.Text("main.status.disconnectRequested"))
        except Exception:
            pass

    def __HandleConnectFromButton(self, button: ttk.Button) -> None:
        BusyButtonTask(
            button,
            work=lambda: self.twitchService.Start(),
            onSuccess=lambda _: self.__SetStatus(self._localizer.Text("main.status.connectRequested")),
            onError=lambda error: self.__ShowErrorDialog(self._localizer.Text("main.dialog.twitch.title"), error),
            uiScheduler=self._uiScheduler,
            busyText="Connecting...",
        ).Invoke()

    def __HandleDisconnectFromButton(self, button: ttk.Button) -> None:
        BusyButtonTask(
            button,
            work=lambda: self.twitchService.Stop(),
            onSuccess=lambda _: self.__SetStatus(self._localizer.Text("main.status.disconnectRequested")),
            onError=lambda _: None,
            uiScheduler=self._uiScheduler,
            busyText="Disconnecting...",
        ).Invoke()

    def __ShowErrorDialog(self, title: str, error: Exception) -> None:
        try:
            messagebox.showerror(str(title or "Error"), str(error))
        except Exception:
            pass

    def __SetStatus(self, text: str) -> None:
        safeText = str(text or "")
        if self._uiScheduler is not None and not self._uiScheduler.IsUiThread():
            self._uiScheduler.Post(lambda: self.__SetStatus(safeText))
            return
        if self._statusVar is not None:
            self._statusVar.set(safeText)

    def UpdatePreview(self, votes: List[Tuple[str, int]]) -> None:
        """Mirror overlay votes into the embedded preview canvas.

        Args:
            votes (list[tuple[str, int]]): entries to display, e.g. [("Option A", 3)].

        Returns:
            None
        """

        return

    def ClearPreview(self) -> None:
        """Clear the embedded preview canvas.

        Returns:
            None
        """

        return

    def SetBorderlessOption(self, enabled: bool) -> None:
        """Sync the borderless option checkbox to the provided value.

        Args:
            enabled (bool): borderless toggle.

        Returns:
            None
        """

        return

    def SetTwitchStatus(self, status: str, message: str = "") -> None:
        safeStatus = str(status or "")
        safeMessage = str(message or "")
        summary = safeMessage if safeMessage else safeStatus
        if self._uiScheduler is not None and not self._uiScheduler.IsUiThread():
            self._uiScheduler.Post(lambda: self.SetTwitchStatus(safeStatus, safeMessage))
            return
        if self._twitchStatusVar is not None:
            self._twitchStatusVar.set(self._localizer.Text("main.twitch.prefix", summary=summary))
