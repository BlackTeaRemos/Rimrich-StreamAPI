import tkinter as tk
import threading
from typing import List, Optional, Tuple

from src.events.close_overlay_event import CloseOverlayEvent
from src.core.events.event_bus import EventBus
from src.features.overlay.drag_controller import DragController
from src.features.overlay.overlay_view import OverlayView
from src.features.overlay.renderer import Renderer
from src.features.overlay.view_factory import ViewFactory
from src.core.localization.localizer_provider import LocalizerProvider
from src.window.ui_thread_scheduler import UiThreadScheduler


class Service:
    def __init__(
        self,
        eventBus: EventBus,
        uiScheduler: UiThreadScheduler | None = None,
        localizerProvider: LocalizerProvider | None = None,
    ) -> None:
        self.eventBus = eventBus
        self._uiScheduler = uiScheduler
        self._localizerProvider = localizerProvider
        self._localizer = localizerProvider.Get() if localizerProvider is not None else None
        self._parent: Optional[tk.Tk] = None
        self._uiThreadIdent: Optional[int] = None
        self._window: Optional[tk.Toplevel] = None
        self._view: Optional[OverlayView] = None
        self._votes: List[Tuple[str, int]] = []
        self._voters: List[str] = []
        self._renderer: Optional[Renderer] = None
        self._dragController = DragController()
        self._viewFactory = ViewFactory()
        self._borderlessEnabled = False
        self._chromaEnabled = False
        self._chromaVoterCount = 0
        self._resizeAfterId: str | None = None

    def AttachParent(self, parent: tk.Tk) -> None:
        self._parent = parent
        self._uiThreadIdent = threading.get_ident()

    def __IsUiThread(self) -> bool:
        if self._uiScheduler is not None:
            return self._uiScheduler.IsUiThread()
        if self._uiThreadIdent is None:
            return True
        return threading.get_ident() == self._uiThreadIdent

    def ShowWindow(self, votes: List[Tuple[str, int]], voters: List[str] | None = None) -> None:
        if not self.__IsUiThread():
            safeVotes = list(votes)
            safeVoters = list(voters) if voters is not None else None
            if self._uiScheduler is not None:
                self._uiScheduler.Post(lambda: self.ShowWindow(safeVotes, safeVoters))
                return
            return

        self._votes = votes
        self._voters = voters if voters is not None else []

        if self._localizerProvider is not None:
            self._localizer = self._localizerProvider.Get()

        if self._window is None:
            self._window = tk.Toplevel(self._parent) if self._parent is not None else tk.Toplevel()
            if self._borderlessEnabled:
                self._window.overrideredirect(True)
            self._window.geometry("440x300")
            self._window.configure(bg="#0f0f0f")
            try:
                titleText = self._localizer.Text("overlay.title") if self._localizer is not None else "Stream Votes Overlay"
            except Exception:
                titleText = "Stream Votes Overlay"
            self._window.title(titleText)
            self._window.attributes("-topmost", True)
            try:
                self._window.wm_attributes("-toolwindow", False)
            except Exception:
                pass
            try:
                self._window.resizable(True, True)
            except Exception:
                pass
            self.__ConfigureContents()
            self.__ConfigureBindings()
            self._window.update_idletasks()

        self.__ApplyTheme()
        self.__RenderVotes()

    def CloseWindow(self) -> None:
        if not self.__IsUiThread():
            if self._uiScheduler is not None:
                self._uiScheduler.Post(self.CloseWindow)
                return
            return

        if self._window is None:
            return
        try:
            if self._window.winfo_exists():
                self._window.destroy()
        except Exception:
            pass
        self._window = None
        self._view = None

    def SetBorderless(self, enabled: bool) -> None:
        self._borderlessEnabled = enabled
        if self._window is None:
            return
        try:
            self._window.overrideredirect(enabled)
            self.__ConfigureBindings()
        except Exception:
            pass

    def SetChroma(self, enabled: bool, voterCount: int) -> None:
        self._chromaEnabled = bool(enabled)
        count = int(voterCount)
        if count < 0:
            count = 0
        if count > 3:
            count = 3
        self._chromaVoterCount = count

        if self._window is not None:
            try:
                if self._view is not None:
                    if self._view.header is not None:
                        self._view.header.destroy()
                    if self._view.closeButton is not None:
                        self._view.closeButton.destroy()
                    self._view.canvas.destroy()
            except Exception:
                pass
            self._view = None
            self._renderer = None
            self.__ConfigureContents()
            self.__ConfigureBindings()

        self.__ApplyTheme()
        self.__RenderVotes()

    def __ConfigureContents(self) -> None:
        if self._window is None:
            return
        bgColor = "#00ff00" if self._chromaEnabled else "#0f0f0f"
        controlsVisible = not self._chromaEnabled
        try:
            closeText = self._localizer.Text("overlay.button.close") if self._localizer is not None else "Close"
        except Exception:
            closeText = "Close"

        self._view = self._viewFactory.Build(
            self._window,
            lambda: self.eventBus.Publish(CloseOverlayEvent()),
            bgColor,
            controlsVisible,
            closeText,
        )
        self._renderer = Renderer(self._view.canvas, localizer=self._localizer)

    def __ConfigureBindings(self) -> None:
        if self._window is None:
            return
        self._window.bind("<Escape>", self.__HandleEscape)
        self._window.bind("<Configure>", self.__OnWindowConfigure)

        view = self._view
        if view is None:
            return

        targets: list[tk.Misc] = [view.canvas]
        if view.header is not None:
            targets.insert(0, view.header)

        for target in targets:
            try:
                if self._borderlessEnabled:
                    target.bind("<ButtonPress-1>", self.__StartMove)
                    target.bind("<B1-Motion>", self.__HandleMove)
                else:
                    target.unbind("<ButtonPress-1>")
                    target.unbind("<B1-Motion>")
            except Exception:
                pass

    def __OnWindowConfigure(self, event: tk.Event) -> None:
        if self._window is None:
            return
        try:
            if getattr(event, "widget", None) is not self._window:
                return
        except Exception:
            return

        # Throttle resize re-renders to keep Tk responsive.
        try:
            if self._resizeAfterId is not None:
                self._window.after_cancel(self._resizeAfterId)
        except Exception:
            pass

        try:
            self._resizeAfterId = self._window.after(60, self.__RenderVotes)
        except Exception:
            self._resizeAfterId = None

    def __HandleEscape(self, event: tk.Event) -> None:
        self.eventBus.Publish(CloseOverlayEvent())

    def __StartMove(self, event: tk.Event) -> None:
        if self._window is None:
            return
        if not self._borderlessEnabled:
            return
        self._dragController.Begin(self._window, event)

    def __HandleMove(self, event: tk.Event) -> None:
        if self._window is None:
            return
        if not self._borderlessEnabled:
            return
        self._dragController.Drag(self._window, event)

    def __RenderVotes(self) -> None:
        if self._renderer is None or self._view is None:
            return
        try:
            if not self._view.canvas.winfo_exists():
                return
        except Exception:
            return

        self._renderer.ConfigureChroma(self._chromaEnabled, self._chromaVoterCount)
        limitedVoters = self._voters[: self._chromaVoterCount]
        self._renderer.Render(self._votes, limitedVoters)

    def __ApplyTheme(self) -> None:
        bgColor = "#00ff00" if self._chromaEnabled else "#0f0f0f"
        try:
            if self._window is not None:
                self._window.configure(bg=bgColor)
            if self._view is not None:
                self._view.canvas.configure(bg=bgColor)
                if self._view.header is not None:
                    self._view.header.configure(bg=bgColor)
                if self._view.closeButton is not None:
                    self._view.closeButton.configure(
                        bg="#2b2b2b" if not self._chromaEnabled else "#00ff00",
                        activebackground="#3a3a3a" if not self._chromaEnabled else "#00ff00",
                    )
        except Exception:
            pass
