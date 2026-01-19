import tkinter as tk
from tkinter import ttk
import threading
from typing import List, Tuple

from src.window.ui_thread_scheduler import UiThreadScheduler
from src.window.theme import Theme
from src.core.localization.localizer_provider import LocalizerProvider


class ChatWindowService:

    def __init__(
        self,
        uiScheduler: UiThreadScheduler | None = None,
        localizerProvider: LocalizerProvider | None = None,
    ) -> None:
        self._uiScheduler = uiScheduler
        self._localizerProvider = localizerProvider
        self._localizer = localizerProvider.Get() if localizerProvider is not None else None
        self._window: tk.Toplevel | None = None  # chat window
        self._listbox: tk.Listbox | None = None  # messages list
        self._statusLabel: tk.Label | None = None  # status text
        self._notebook: ttk.Notebook | None = None  # tab control
        self._messages: List[Tuple[str, str]] = []  # buffered messages
        self._lock = threading.Lock()

    def ShowWindow(self, parent: tk.Tk) -> None:

        if self._window is not None and self._window.winfo_exists():
            self._window.lift()
            return

        if self._localizerProvider is not None:
            self._localizer = self._localizerProvider.Get()

        self._window = tk.Toplevel(parent)
        self._window.title(self.__Text("chat.title", default="Chat Log"))
        self._window.geometry("380x360")
        Theme.Apply(self._window)
        self._window.transient(parent)
        self._window.resizable(True, True)

        palette = Theme.Palette

        header = tk.Frame(self._window, bg=palette.surface)
        header.pack(fill=tk.X, padx=10, pady=(10, 6))

        title = tk.Label(
            header,
            text=self.__Text("chat.header.title", default="Recent messages"),
            bg=palette.surface,
            fg=palette.text,
            font=("Segoe UI Semibold", 12),
        )
        title.pack(side=tk.LEFT)

        closeButton = tk.Button(
            header,
            text=self.__Text("chat.button.close", default="Close"),
            command=self.__HandleClose,
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

        self._notebook = ttk.Notebook(self._window)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        messagesTab = tk.Frame(self._notebook, bg=palette.surfaceDeep)
        self._notebook.add(messagesTab, text=self.__Text("chat.tab.messages", default="Messages"))

        self._listbox = tk.Listbox(messagesTab, bg=palette.surfaceDeep, fg=palette.text, selectbackground=palette.button, highlightthickness=0)
        self._listbox.pack(fill=tk.BOTH, expand=True, padx=0, pady=6)

        statusTab = tk.Frame(self._notebook, bg=palette.surfaceDeep)
        self._notebook.add(statusTab, text=self.__Text("chat.tab.status", default="Status"))
        self._statusLabel = tk.Label(
            statusTab,
            text=self.__Text("chat.status.waiting", default="Waiting for connection"),
            bg=palette.surfaceDeep,
            fg=palette.textMuted,
            anchor="w",
        )
        self._statusLabel.pack(fill=tk.X, padx=6, pady=6)

        self.__RefreshView()

    def __Text(self, key: str, default: str) -> str:
        if self._localizer is None:
            return default
        try:
            return self._localizer.Text(key)
        except Exception:
            return default

    def __HandleClose(self) -> None:
        """Destroy the chat window and clear internal references.

        Returns:
            None
        """

        if self._window is None:
            return
        try:
            if self._window.winfo_exists():
                self._window.destroy()
        except Exception:
            pass
        self._window = None
        self._listbox = None
        self._statusLabel = None
        self._notebook = None

    def RecordMessage(self, user: str, content: str) -> None:
        """Store an incoming chat message and refresh the view.

        Args:
            user (str): author name, e.g. "viewer".
            content (str): chat text, e.g. "hello".

        Returns:
            None
        """

        safeUser = user if user is not None else ""
        safeContent = content if content is not None else ""
        with self._lock:
            self._messages.append((safeUser, safeContent))
            self._messages = self._messages[-200:]

        if self._uiScheduler is not None and not self._uiScheduler.IsUiThread():
            self._uiScheduler.Post(self.__RefreshView)
            return
        self.__RefreshView()

    def SetStatus(self, text: str) -> None:
        """Update the status text shown in the status tab.

        Args:
            text (str): status message, e.g. "Connected".

        Returns:
            None
        """

        safeText = str(text or "")
        if self._uiScheduler is not None and not self._uiScheduler.IsUiThread():
            self._uiScheduler.Post(lambda: self.SetStatus(safeText))
            return
        if self._statusLabel is None:
            return
        try:
            self._statusLabel.config(text=safeText)
        except Exception:
            pass

    def __RefreshView(self) -> None:
        """Redraw the messages list from the internal buffer.

        Returns:
            None
        """

        if self._listbox is None:
            return
        try:
            with self._lock:
                snapshot = list(self._messages)
            self._listbox.delete(0, tk.END)
            for user, content in snapshot:
                display = f"{user}: {content}" if user else content
                self._listbox.insert(tk.END, display)
        except Exception:
            pass
