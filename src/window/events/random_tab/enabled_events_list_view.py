from __future__ import annotations

import tkinter as tk
from typing import Callable, List, Tuple

from src.window.events.random_tab.enabled_events_list_state import EnabledEventRow
from src.window.theme import Theme
from src.core.localization.localizer import Localizer


class EnabledEventsListView:
    def __init__(self, localizer: Localizer | None = None) -> None:
        self._localizer = localizer
        self._filterVar: tk.StringVar | None = None
        self._listbox: tk.Listbox | None = None
        self._itemKeys: List[Tuple[str, str]] = []
        self._rowBackgrounds: List[str] = []
        self._hoverIndex: int | None = None

    def Close(self) -> None:
        self._filterVar = None
        self._listbox = None
        self._itemKeys = []
        self._rowBackgrounds = []
        self._hoverIndex = None

    def GetListbox(self) -> tk.Listbox | None:
        return self._listbox

    def GetFilterQuery(self) -> str:
        if self._filterVar is None:
            return ""
        return str(self._filterVar.get() or "").strip().lower()

    def Build(
        self,
        parent: tk.Frame,
        onFilterChanged: Callable[[], None],
        onSelectionChanged: Callable[[Tuple[str, str] | None], None],
        onMouseWheel: Callable[[tk.Event], str | None],
        onToggleRequested: Callable[[tk.Event], str | None],
    ) -> None:
        palette = Theme.Palette

        header = tk.Frame(parent, bg=palette.surfaceDeep)
        header.pack(fill=tk.X, pady=(0, 6))
        tk.Label(
            header,
            text=self.__Text("events.random.enabled.search", default="Search"),
            bg=palette.surfaceDeep,
            fg=palette.textMuted,
        ).pack(side=tk.LEFT, padx=(0, 6))
        self._filterVar = tk.StringVar(value="")
        filterEntry = tk.Entry(header, textvariable=self._filterVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
        filterEntry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        filterEntry.bind("<KeyRelease>", lambda event: onFilterChanged())

        tk.Label(
            header,
            text=self.__Text("events.random.enabled.toggleHint", default="Double-click or Space to toggle"),
            bg=palette.surfaceDeep,
            fg=palette.textFaint,
        ).pack(side=tk.RIGHT, padx=(8, 0))

        body = tk.Frame(parent, bg=palette.surfaceDeep)
        body.pack(fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(
            body,
            bg=palette.surfaceDeep,
            fg=palette.text,
            # Dark selection highlight (not blue) so state styling remains readable.
            selectbackground=palette.button,
            selectforeground=palette.text,
            highlightthickness=0,
            width=34,
            activestyle="none",
            font=("Segoe UI", 10),
            exportselection=False,
        )
        scrollbar = tk.Scrollbar(body, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox.bind("<MouseWheel>", onMouseWheel, add="+")
        listbox.bind("<Button-4>", onMouseWheel, add="+")
        listbox.bind("<Button-5>", onMouseWheel, add="+")

        def onSingleClick(event: tk.Event) -> None:
            # Let Tk update selection naturally; we only mirror selection into the view model.
            try:
                index = int(listbox.nearest(int(getattr(event, "y", 0))))
                if index >= 0:
                    listbox.selection_clear(0, tk.END)
                    listbox.selection_set(index)
                    listbox.activate(index)
            except Exception:
                pass

        def onSelect(event: tk.Event) -> None:
            try:
                selection = listbox.curselection()
                if not selection:
                    onSelectionChanged(None)
                    return
                index = int(selection[0])
                if 0 <= index < len(self._itemKeys):
                    onSelectionChanged(self._itemKeys[index])
                else:
                    onSelectionChanged(None)
            except Exception:
                onSelectionChanged(None)

        def onDoubleClick(event: tk.Event) -> str | None:
            result = onToggleRequested(event)
            return result or "break"

        listbox.bind("<Button-1>", onSingleClick, add="+")
        listbox.bind("<<ListboxSelect>>", onSelect, add="+")
        listbox.bind("<Double-Button-1>", onDoubleClick, add="+")
        listbox.bind("<Return>", onToggleRequested, add="+")
        listbox.bind("<space>", onToggleRequested, add="+")

        def restoreHover() -> None:
            if self._hoverIndex is None:
                return
            if self._hoverIndex < 0 or self._hoverIndex >= len(self._rowBackgrounds):
                self._hoverIndex = None
                return
            try:
                listbox.itemconfig(self._hoverIndex, background=self._rowBackgrounds[self._hoverIndex])
            except Exception:
                pass
            self._hoverIndex = None

        def onMotion(event: tk.Event) -> None:
            try:
                index = int(listbox.nearest(int(getattr(event, "y", 0))))
            except Exception:
                return

            if index < 0 or index >= len(self._rowBackgrounds):
                restoreHover()
                return

            if self._hoverIndex == index:
                return

            restoreHover()
            try:
                selection = listbox.curselection()
                if selection and int(selection[0]) == index:
                    return
            except Exception:
                pass

            try:
                # Hover uses a consistent highlight, but we restore the per-row state color on leave.
                listbox.itemconfig(index, background=palette.buttonHover)
                self._hoverIndex = index
            except Exception:
                self._hoverIndex = None

        listbox.bind("<Motion>", onMotion, add="+")
        listbox.bind("<Leave>", lambda event: restoreHover(), add="+")

        self._listbox = listbox

    def __Text(self, key: str, default: str, **formatArgs: object) -> str:
        if self._localizer is None:
            return default
        try:
            return self._localizer.Text(key, **formatArgs)
        except Exception:
            return default

    def Render(
        self,
        rows: List[EnabledEventRow],
        preferredSelection: Tuple[str, str] | None,
        preserveScroll: bool,
    ) -> List[Tuple[str, str]]:
        listbox = self._listbox
        if listbox is None:
            return []

        palette = Theme.Palette

        preservedScroll = None
        if preserveScroll:
            try:
                preservedScroll = listbox.yview()
            except Exception:
                preservedScroll = None

        query = self.GetFilterQuery()
        visibleRows = [row for row in rows if (not query) or (query in row.label.lower())]

        try:
            listbox.delete(0, tk.END)
            self._itemKeys = []
            self._rowBackgrounds = []
            self._hoverIndex = None
            for row in visibleRows:
                index = listbox.size()
                key = (row.kind, row.identifier)

                selected = preferredSelection is not None and key == preferredSelection
                selectionMark = "▶ " if selected else "  "
                overrideMark = "▣ " if row.overridden else "  "
                stateMark = "[ON] " if row.enabled else "[OFF] "
                listbox.insert(tk.END, selectionMark + overrideMark + stateMark + row.label)

                # Darker tone styling (no bright blue):
                # - enabled: slightly lighter surface
                # - disabled: deep surface
                # - overridden: appears "pressed" via button surfaces + marker
                if row.overridden and row.enabled:
                    background = palette.buttonHover
                    foreground = palette.text
                elif row.overridden and (not row.enabled):
                    background = palette.button
                    foreground = palette.textMuted
                elif row.enabled:
                    background = palette.surfaceAlt
                    foreground = palette.text
                else:
                    background = palette.surfaceDeep
                    foreground = palette.textFaint

                self._rowBackgrounds.append(background)
                try:
                    listbox.itemconfig(index, foreground=foreground, background=background)
                except Exception:
                    pass
                self._itemKeys.append((row.kind, row.identifier))
        except Exception:
            return []

        if preferredSelection is not None:
            try:
                newIndex = next((number for number, item in enumerate(self._itemKeys) if item == preferredSelection), None)
                if newIndex is not None:
                    listbox.selection_clear(0, tk.END)
                    listbox.selection_set(int(newIndex))
                    listbox.activate(int(newIndex))
                    listbox.see(int(newIndex))
            except Exception:
                pass

        if preservedScroll is not None:
            try:
                listbox.yview_moveto(float(preservedScroll[0]))
            except Exception:
                pass

        return list(self._itemKeys)
