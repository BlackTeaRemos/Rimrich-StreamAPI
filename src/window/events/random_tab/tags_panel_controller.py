from __future__ import annotations

import tkinter as tk
from typing import Callable, Dict, List

from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.game_events.templates.game_event_template_catalog_service import GameEventTemplateCatalogService
from src.window.theme import Theme
from src.core.localization.localizer import Localizer


class TagsPanelController:
    def __init__(
        self,
        catalogService: GameEventCatalogService,
        templateCatalogService: GameEventTemplateCatalogService | None,
        onSelectionChanged: Callable[[], None],
        localizer: Localizer | None = None,
    ) -> None:
        self._catalogService = catalogService
        self._templateCatalogService = templateCatalogService
        self._onSelectionChanged = onSelectionChanged
        self._localizer = localizer

        self._tagVars: Dict[str, tk.BooleanVar] = {}
        self._tagButtons: Dict[str, tk.Button] = {}
        self._tagsContainer: tk.Frame | None = None
        self._tagsCanvas: tk.Canvas | None = None
        self._filterVar: tk.StringVar | None = None
        self._allTags: List[str] = []

    def Build(self, parent: tk.Frame) -> None:
        palette = Theme.Palette

        header = tk.Frame(parent, bg=palette.surfaceDeep)
        header.pack(fill=tk.X, pady=(0, 6))

        tk.Label(header, text=self.__Text("events.random.tags.search", default="Search"), bg=palette.surfaceDeep, fg=palette.textMuted).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        self._filterVar = tk.StringVar(value="")
        filterEntry = tk.Entry(header, textvariable=self._filterVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
        filterEntry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        filterEntry.bind("<KeyRelease>", lambda event: self.__RenderTags())

        buttons = tk.Frame(header, bg=palette.surfaceDeep)
        buttons.pack(side=tk.RIGHT, padx=(8, 0))
        tk.Button(
            buttons,
            text=self.__Text("events.random.tags.all", default="All"),
            command=lambda: self.__SetAll(True),
            bg=palette.button,
            fg=palette.text,
            activebackground=palette.buttonHover,
            activeforeground=palette.text,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            width=5,
        ).pack(side=tk.LEFT)
        tk.Button(
            buttons,
            text=self.__Text("events.random.tags.none", default="None"),
            command=lambda: self.__SetAll(False),
            bg=palette.button,
            fg=palette.text,
            activebackground=palette.buttonHover,
            activeforeground=palette.text,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            width=6,
        ).pack(side=tk.LEFT, padx=(6, 0))

        body = tk.Frame(parent, bg=palette.surfaceDeep)
        body.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(body, bg=palette.surfaceDeep, highlightthickness=0)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=palette.surfaceDeep)
        scrollable.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self._tagsCanvas = canvas
        self._tagsContainer = scrollable

        canvas.bind("<MouseWheel>", self.__OnTagsMouseWheel, add="+")
        canvas.bind("<Button-4>", self.__OnTagsMouseWheel, add="+")
        canvas.bind("<Button-5>", self.__OnTagsMouseWheel, add="+")
        scrollable.bind("<MouseWheel>", self.__OnTagsMouseWheel, add="+")
        scrollable.bind("<Button-4>", self.__OnTagsMouseWheel, add="+")
        scrollable.bind("<Button-5>", self.__OnTagsMouseWheel, add="+")

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.ReloadTags()

    def Close(self) -> None:
        self._tagVars = {}
        self._tagButtons = {}
        self._tagsContainer = None
        self._tagsCanvas = None
        self._filterVar = None
        self._allTags = []

    def GetSelectedTags(self) -> List[str]:
        return [tag for tag, variable in self._tagVars.items() if variable.get()]

    def ReloadTags(self) -> None:
        self._tagVars = {}
        self._tagButtons = {}
        self._allTags = []

        tags = set()
        try:
            for definition in self._catalogService.GetAll():
                if bool(getattr(definition, "hidden", False)):
                    continue
                for tag in definition.tags:
                    if str(tag).strip():
                        tags.add(str(tag))
        except Exception:
            pass

        if self._templateCatalogService is not None:
            try:
                for template in self._templateCatalogService.GetAll():
                    if bool(getattr(template, "hidden", False)):
                        continue
                    for tag in template.tags:
                        if str(tag).strip():
                            tags.add(str(tag))
            except Exception:
                pass

        self._allTags = sorted(tags)
        for tag in self._allTags:
            self._tagVars[tag] = tk.BooleanVar(value=False)

        self.__RenderTags(rebuild=True)
        self._onSelectionChanged()

    def __SetAll(self, enabled: bool) -> None:
        for variable in self._tagVars.values():
            try:
                variable.set(bool(enabled))
            except Exception:
                pass
        self._onSelectionChanged()
        self.__UpdateAllTagButtonStyles()

    def __RenderTags(self, rebuild: bool = False) -> None:
        container = self._tagsContainer
        if container is None:
            return
        palette = Theme.Palette

        query = ""
        if self._filterVar is not None:
            query = str(self._filterVar.get() or "").strip().lower()

        visibleTags = [tag for tag in self._allTags if (not query) or (query in tag.lower())]

        if rebuild:
            for widget in list(container.winfo_children()):
                try:
                    widget.destroy()
                except Exception:
                    continue
            self._tagButtons = {}

        # Ensure buttons exist (create once, then only restyle/re-grid to avoid flicker).
        if (not self._tagButtons) or rebuild:
            def toggleTag(tagValue: str) -> None:
                variable = self._tagVars.get(tagValue)
                if variable is None:
                    variable = tk.BooleanVar(value=False)
                    self._tagVars[tagValue] = variable
                try:
                    variable.set(not bool(variable.get()))
                except Exception:
                    return

                self._onSelectionChanged()
                self.__UpdateTagButtonStyle(tagValue)

            for tag in self._allTags:
                if tag in self._tagButtons:
                    continue

                button = tk.Button(
                    container,
                    text=tag,
                    command=lambda tagValue=tag: toggleTag(tagValue),
                    bg=palette.surfaceAlt,
                    fg=palette.textMuted,
                    activebackground=palette.buttonHover,
                    activeforeground=palette.text,
                    relief=tk.RAISED,
                    borderwidth=1,
                    highlightthickness=0,
                    padx=10,
                    pady=4,
                    anchor="w",
                )

                def onEnter(event: tk.Event, widget: tk.Button = button, tagValue: str = tag) -> None:
                    try:
                        selected = self.__IsTagSelected(tagValue)
                        widget.configure(bg=palette.buttonHover if selected else palette.button)
                    except Exception:
                        pass

                def onLeave(event: tk.Event, widget: tk.Button = button, tagValue: str = tag) -> None:
                    try:
                        selected = self.__IsTagSelected(tagValue)
                        widget.configure(bg=palette.buttonHover if selected else palette.surfaceAlt)
                    except Exception:
                        pass

                button.bind("<Enter>", onEnter)
                button.bind("<Leave>", onLeave)
                self.__BindTagScroll(button)
                self._tagButtons[tag] = button

            try:
                container.grid_columnconfigure(0, weight=1)
                container.grid_columnconfigure(1, weight=1)
            except Exception:
                pass

        # Apply filter by re-gridding visible tags only.
        for tagValue, button in self._tagButtons.items():
            try:
                button.grid_remove()
            except Exception:
                pass

        if not visibleTags:
            # Keep a single placeholder label if no tags match.
            placeholder = getattr(self, "_noMatchLabel", None)
            if placeholder is None or not isinstance(placeholder, tk.Label) or not placeholder.winfo_exists():
                placeholder = tk.Label(
                    container,
                    text=self.__Text("events.random.tags.noMatch", default="No tags match"),
                    bg=palette.surfaceDeep,
                    fg=palette.textFaint,
                    anchor="w",
                )
                setattr(self, "_noMatchLabel", placeholder)
                self.__BindTagScroll(placeholder)
            try:
                placeholder.grid(row=0, column=0, columnspan=2, sticky="ew", padx=6, pady=6)
            except Exception:
                pass
            return

        # Hide placeholder if present.
        placeholder = getattr(self, "_noMatchLabel", None)
        if placeholder is not None:
            try:
                placeholder.grid_remove()
            except Exception:
                pass

        for index, tagValue in enumerate(visibleTags):
            button = self._tagButtons.get(tagValue)
            if button is None:
                continue

            self.__UpdateTagButtonStyle(tagValue)
            try:
                button.grid(row=index // 2, column=index % 2, sticky="ew", padx=6, pady=4)
            except Exception:
                continue

    def __Text(self, key: str, default: str, **formatArgs: object) -> str:
        if self._localizer is None:
            return default
        try:
            return self._localizer.Text(key, **formatArgs)
        except Exception:
            return default

    def __IsTagSelected(self, tagValue: str) -> bool:
        variable = self._tagVars.get(tagValue)
        if variable is None:
            return False
        try:
            return bool(variable.get())
        except Exception:
            return False

    def __UpdateTagButtonStyle(self, tagValue: str) -> None:
        container = self._tagsContainer
        if container is None:
            return
        palette = Theme.Palette
        button = self._tagButtons.get(tagValue)
        if button is None:
            return

        selected = self.__IsTagSelected(tagValue)
        background = palette.buttonHover if selected else palette.surfaceAlt
        foreground = palette.text if selected else palette.textMuted
        relief = tk.SUNKEN if selected else tk.RAISED
        try:
            button.configure(bg=background, fg=foreground, activebackground=palette.buttonHover, activeforeground=palette.text, relief=relief)
        except Exception:
            pass

    def __UpdateAllTagButtonStyles(self) -> None:
        for tagValue in list(self._tagButtons.keys()):
            self.__UpdateTagButtonStyle(tagValue)

    def __BindTagScroll(self, widget: tk.Widget) -> None:
        widget.bind("<MouseWheel>", self.__OnTagsMouseWheel, add="+")
        widget.bind("<Button-4>", self.__OnTagsMouseWheel, add="+")
        widget.bind("<Button-5>", self.__OnTagsMouseWheel, add="+")

    def __OnTagsMouseWheel(self, event: tk.Event) -> str | None:
        canvas = self._tagsCanvas
        if canvas is None:
            return None

        delta = getattr(event, "delta", 0)
        if isinstance(delta, int) and delta != 0:
            units = int(-delta / 120)
            if units == 0:
                units = -1 if delta > 0 else 1
            canvas.yview_scroll(units, "units")
            return "break"

        button = getattr(event, "num", None)
        if button == 4:
            canvas.yview_scroll(-3, "units")
            return "break"
        if button == 5:
            canvas.yview_scroll(3, "units")
            return "break"

        return None
