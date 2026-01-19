from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import time
from typing import Callable, List, Optional

from src.window.events.catalog_item import CatalogItem
from src.window.theme import Theme
from src.core.localization.localizer import Localizer


class CatalogTab:
    def __init__(
        self,
        onSelectionChanged: Callable[[], None],
        onTestAllRequested: Optional[Callable[[], None]] = None,
        localizer: Localizer | None = None,
    ) -> None:
        self._onSelectionChanged = onSelectionChanged
        self._onTestAllRequested = onTestAllRequested
        self._localizer = localizer
        self._tree: ttk.Treeview | None = None
        self._details: tk.Text | None = None
        self._filterVar: tk.StringVar | None = None
        self._showNormalVar: tk.BooleanVar | None = None
        self._showRandomVar: tk.BooleanVar | None = None
        self._countLabel: tk.Label | None = None
        self._allItems: List[CatalogItem] = []
        self._visibleIndices: List[int] = []

        self._sortColumn: str = "label"
        self._sortDescending: bool = False

        self._copyJsonButton: ttk.Button | None = None
        self._copyIdButton: ttk.Button | None = None
        self._testAllButton: ttk.Button | None = None
        self._testAllClickCount: int = 0
        self._testAllLastClickAt: float = 0.0

    def Build(self, parent: tk.Frame) -> None:
        palette = Theme.Palette
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=2)
        parent.rowconfigure(0, weight=1)

        left = tk.Frame(parent, bg=palette.surfaceDeep)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        right = tk.Frame(parent, bg=palette.surfaceDeep)
        right.grid(row=0, column=1, sticky="nsew")

        filterRow = tk.Frame(left, bg=palette.surfaceDeep)
        filterRow.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(filterRow, text=self.__Text("events.catalog.search", default="Search"), bg=palette.surfaceDeep, fg=palette.textMuted).pack(side=tk.LEFT)
        self._filterVar = tk.StringVar(value="")
        filterEntry = tk.Entry(filterRow, textvariable=self._filterVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
        filterEntry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))
        filterEntry.bind("<KeyRelease>", lambda event: self.__ApplyFilter())

        self._countLabel = tk.Label(filterRow, text="0/0", bg=palette.surfaceDeep, fg=palette.textFaint)
        self._countLabel.pack(side=tk.RIGHT, padx=(8, 0))

        filterKinds = tk.Frame(left, bg=palette.surfaceDeep)
        filterKinds.pack(fill=tk.X, padx=8, pady=(0, 8))
        self._showNormalVar = tk.BooleanVar(value=True)
        self._showRandomVar = tk.BooleanVar(value=True)
        normalToggle = tk.Checkbutton(
            filterKinds,
            text=self.__Text("events.catalog.kind.normal", default="Normal"),
            variable=self._showNormalVar,
            command=lambda: self.__ApplyFilter(preserveSelection=True),
            bg=palette.surfaceDeep,
            fg=palette.text,
            activebackground=palette.surfaceDeep,
            activeforeground=palette.text,
            selectcolor=palette.button,
            highlightthickness=0,
        )
        normalToggle.pack(side=tk.LEFT)
        randomToggle = tk.Checkbutton(
            filterKinds,
            text=self.__Text("events.catalog.kind.random", default="Random"),
            variable=self._showRandomVar,
            command=lambda: self.__ApplyFilter(preserveSelection=True),
            bg=palette.surfaceDeep,
            fg=palette.text,
            activebackground=palette.surfaceDeep,
            activeforeground=palette.text,
            selectcolor=palette.button,
            highlightthickness=0,
        )
        randomToggle.pack(side=tk.LEFT, padx=(10, 0))

        listFrame = tk.Frame(left, bg=palette.surfaceDeep)
        listFrame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        treeScrollbar = ttk.Scrollbar(listFrame, orient="vertical")
        treeScrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("type", "label", "id", "cost", "prob")
        self._tree = ttk.Treeview(listFrame, columns=columns, show="headings", selectmode="browse")
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._tree.configure(yscrollcommand=treeScrollbar.set)
        treeScrollbar.config(command=self._tree.yview)

        self._tree.heading("type", text=self.__Text("events.catalog.column.type", default="Type"), command=lambda: self.__SortBy("type"))
        self._tree.heading("label", text=self.__Text("events.catalog.column.label", default="Label"), command=lambda: self.__SortBy("label"))
        self._tree.heading("id", text=self.__Text("events.catalog.column.id", default="Id"), command=lambda: self.__SortBy("id"))
        self._tree.heading("cost", text=self.__Text("events.catalog.column.cost", default="Cost"), command=lambda: self.__SortBy("cost"))
        self._tree.heading("prob", text=self.__Text("events.catalog.column.prob", default="Prob"), command=lambda: self.__SortBy("prob"))

        self._tree.column("type", width=70, anchor="w", stretch=False)
        self._tree.column("label", width=260, anchor="w", stretch=True)
        self._tree.column("id", width=140, anchor="w", stretch=False)
        self._tree.column("cost", width=60, anchor="e", stretch=False)
        self._tree.column("prob", width=70, anchor="e", stretch=False)

        self._tree.bind("<<TreeviewSelect>>", lambda event: self._onSelectionChanged())
        self._tree.bind("<Double-Button-1>", lambda event: self.__CopySelectedId())

        try:
            self._tree.tag_configure("even", background=palette.surfaceDeep)
            self._tree.tag_configure("odd", background=palette.surface)
        except Exception:
            pass

        detailsHeader = tk.Frame(right, bg=palette.surfaceDeep)
        detailsHeader.pack(fill=tk.X, padx=8, pady=(8, 2))

        detailsTitle = tk.Label(detailsHeader, text=self.__Text("events.catalog.details.title", default="Definition"), bg=palette.surfaceDeep, fg=palette.text, anchor="w")
        detailsTitle.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._copyIdButton = ttk.Button(
            detailsHeader,
            text=self.__Text("events.catalog.button.copyId", default="Copy Id"),
            command=self.__CopySelectedId,
            style="Neutral.TButton",
        )
        self._copyIdButton.pack(side=tk.RIGHT)
        self._copyJsonButton = ttk.Button(
            detailsHeader,
            text=self.__Text("events.catalog.button.copyJson", default="Copy JSON"),
            command=self.__CopyDetails,
            style="Neutral.TButton",
        )
        self._copyJsonButton.pack(side=tk.RIGHT, padx=(0, 8))

        self._testAllButton = ttk.Button(
            detailsHeader,
            text=self.__Text("events.catalog.button.testAll.ready", default="Test All (x5)"),
            command=self.__HandleTestAllClicked,
            style="Accent.TButton",
        )
        self._testAllButton.pack(side=tk.RIGHT, padx=(0, 8))

        detailsFrame = tk.Frame(right, bg=palette.button)
        detailsFrame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        scrollbar = tk.Scrollbar(detailsFrame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._details = tk.Text(
            detailsFrame,
            bg=palette.button,
            fg=palette.textMuted,
            insertbackground=palette.text,
            wrap=tk.WORD,
            relief=tk.FLAT,
            yscrollcommand=scrollbar.set,
            font=("Cascadia Mono", 9),
        )
        self._details.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self._details.yview)
        try:
            self._details.configure(state=tk.DISABLED)
        except Exception:
            pass

    def __CopyDetails(self) -> None:
        if self._details is None:
            return
        try:
            text = self._details.get("1.0", tk.END)
        except Exception:
            return
        root = None
        try:
            root = self._details.winfo_toplevel()
        except Exception:
            root = None
        if root is None:
            return
        try:
            root.clipboard_clear()
            root.clipboard_append(text.strip())
        except Exception:
            pass

    def __CopySelectedId(self) -> None:
        selectedIndex = self.GetSelectedIndex()
        if selectedIndex is None:
            return
        if selectedIndex < 0 or selectedIndex >= len(self._allItems):
            return
        item = self._allItems[selectedIndex]
        identifier = ""
        try:
            if item.kind == "event":
                identifier = str(item.entry.definition.eventId)
            else:
                identifier = str(item.entry.definition.templateId)
        except Exception:
            identifier = ""
        if identifier.strip() == "":
            return
        root = None
        try:
            if self._tree is not None:
                root = self._tree.winfo_toplevel()
        except Exception:
            root = None
        if root is None:
            return
        try:
            root.clipboard_clear()
            root.clipboard_append(identifier)
        except Exception:
            pass

    def SetItems(self, items: List[CatalogItem]) -> None:
        self._allItems = list(items)
        self.__ApplyFilter(preserveSelection=True)

    def __SortBy(self, column: str) -> None:
        if column == self._sortColumn:
            self._sortDescending = not self._sortDescending
        else:
            self._sortColumn = column
            self._sortDescending = False
        self.__ApplyFilter(preserveSelection=True)

    def __ApplyFilter(self, preserveSelection: bool = False) -> None:
        tree = self._tree
        if tree is None:
            return

        preservedIndex: int | None = None
        if preserveSelection:
            preservedIndex = self.GetSelectedIndex()

        query = ""
        if self._filterVar is not None:
            query = str(self._filterVar.get() or "").strip().lower()

        showNormal = True
        showRandom = True
        if self._showNormalVar is not None:
            showNormal = bool(self._showNormalVar.get())
        if self._showRandomVar is not None:
            showRandom = bool(self._showRandomVar.get())

        self._visibleIndices = []
        for index, item in enumerate(self._allItems):
            if item.kind == "event" and not showNormal:
                continue
            if item.kind == "template" and not showRandom:
                continue
            text = self.__BuildSearchText(item).lower()
            if (not query) or (query in text):
                self._visibleIndices.append(index)

        def sortKey(itemIndex: int) -> object:
            item = self._allItems[itemIndex]
            try:
                if self._sortColumn == "type":
                    return "0" if item.kind == "event" else "1"
                if self._sortColumn == "id":
                    return str(item.entry.definition.eventId if item.kind == "event" else item.entry.definition.templateId).lower()
                if self._sortColumn == "cost":
                    return float(getattr(item.entry.definition, "cost", 0) or 0)
                if self._sortColumn == "prob":
                    return float(getattr(item.entry.definition, "probability", 0) or 0)
                return str(item.entry.definition.label).lower()
            except Exception:
                return ""

        self._visibleIndices.sort(key=sortKey, reverse=bool(self._sortDescending))

        try:
            for child in tree.get_children(""):
                tree.delete(child)
            for itemIndex in self._visibleIndices:
                item = self._allItems[itemIndex]
                kindText = (
                    self.__Text("events.catalog.kind.normal", default="Normal")
                    if item.kind == "event"
                    else self.__Text("events.catalog.kind.random", default="Random")
                )
                try:
                    definition = item.entry.definition
                    identifier = str(definition.eventId if item.kind == "event" else definition.templateId)
                    label = str(definition.label)
                    cost = str(getattr(definition, "cost", ""))
                    prob = str(getattr(definition, "probability", ""))
                except Exception:
                    identifier = item.Identifier()
                    label = item.DisplayText()
                    cost = ""
                    prob = ""
                rowTag = "even" if (len(tree.get_children("")) % 2) == 0 else "odd"
                tree.insert("", tk.END, iid=str(itemIndex), values=(kindText, label, identifier, cost, prob), tags=(rowTag,))
        except Exception:
            return

        if self._countLabel is not None:
            try:
                self._countLabel.configure(text=f"{len(self._visibleIndices)}/{len(self._allItems)}")
            except Exception:
                pass

        if len(tree.get_children("")) == 0:
            self.ClearDetails(self.__Text("events.catalog.details.noMatching", default="No matching events"))

        if preservedIndex is not None and preservedIndex in self._visibleIndices:
            try:
                tree.selection_set(str(preservedIndex))
                tree.focus(str(preservedIndex))
                tree.see(str(preservedIndex))
            except Exception:
                pass
        else:
            # If selection was filtered out, keep UI consistent.
            try:
                tree.selection_remove(tree.selection())
            except Exception:
                pass

    def __BuildSearchText(self, item: CatalogItem) -> str:
        kindText = (
            self.__Text("events.catalog.kind.normal", default="Normal")
            if item.kind == "event"
            else self.__Text("events.catalog.kind.random", default="Random")
        )
        label = item.Label()
        identifier = item.Identifier()
        return f"{kindText} {label} {identifier}".strip()

    def GetSelectedIndex(self) -> Optional[int]:
        if self._tree is None:
            return None
        selection = self._tree.selection()
        if not selection:
            return None
        try:
            return int(selection[0])
        except Exception:
            return None

    def GetVisibleItemIndicesInDisplayOrder(self) -> List[int]:
        tree = self._tree
        if tree is None:
            return []

        indices: List[int] = []
        try:
            for child in tree.get_children(""):
                try:
                    indices.append(int(child))
                except Exception:
                    continue
        except Exception:
            return []

        return indices

    def SelectFirst(self) -> None:
        if self._tree is None:
            return
        children = self._tree.get_children("")
        if not children:
            return
        first = children[0]
        try:
            self._tree.selection_set(first)
            self._tree.focus(first)
            self._tree.see(first)
        except Exception:
            pass

    def RenderDetailsText(self, text: str) -> None:
        if self._details is None:
            return
        try:
            self._details.configure(state=tk.NORMAL)
        except Exception:
            pass
        self._details.delete("1.0", tk.END)
        self._details.insert(tk.END, text)
        try:
            self._details.configure(state=tk.DISABLED)
        except Exception:
            pass

    def ClearDetails(self, placeholder: str = "No events loaded") -> None:
        self.RenderDetailsText(placeholder)

    def __HandleTestAllClicked(self) -> None:
        if self._onTestAllRequested is None:
            return

        now = time.time()
        if (now - self._testAllLastClickAt) > 6.0:
            self._testAllClickCount = 0
        self._testAllLastClickAt = now

        self._testAllClickCount += 1
        remaining = 5 - self._testAllClickCount

        button = self._testAllButton
        if remaining > 0:
            if button is not None:
                try:
                    button.configure(text=self.__Text("events.catalog.button.testAll.armed", default=f"Test All ({self._testAllClickCount}/5)", count=self._testAllClickCount))
                except Exception:
                    pass
            return

        self._testAllClickCount = 0
        if button is not None:
            try:
                button.configure(text=self.__Text("events.catalog.button.testAll.ready", default="Test All (x5)"))
            except Exception:
                pass

        try:
            self._onTestAllRequested()
        except Exception:
            return

    def __Text(self, key: str, default: str, **formatArgs: object) -> str:
        if self._localizer is None:
            return default
        try:
            return self._localizer.Text(key, **formatArgs)
        except Exception:
            return default
