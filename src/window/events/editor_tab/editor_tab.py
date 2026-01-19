from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List, Optional

from src.core.settings.settings_service import SettingsService
from src.game_events.game_event_definition import GameEventDefinition
from src.game_events.game_event_executor import GameEventExecutor
from src.window.events.editor_tab.game_api_data_source import GameApiDataSource
from src.window.events.editor_tab.editor_event_template import EditorEventTemplate
from src.window.events.editor_tab.editor_template_catalog import EditorTemplateCatalog
from src.window.events.editor_tab.parameters.editor_template_parameter import EditorTemplateParameter
from src.window.theme import Theme
from src.window.rest_api_client import RestApiClient
from src.core.localization.localizer import Localizer
from src.window.busy_button_task import BusyButtonTask


class EditorTab:
    def __init__(
        self,
        settingsService: SettingsService,
        executor: GameEventExecutor,
        apiClient: RestApiClient,
        setStatus: Callable[[str], None],
        localizer: Localizer | None = None,
    ) -> None:
        self._settingsService = settingsService
        self._executor = executor
        self._dataSource = GameApiDataSource(settingsService, apiClient)
        self._setStatus = setStatus
        self._localizer = localizer

        self._templateCatalog = EditorTemplateCatalog()
        self._templates: List[EditorEventTemplate] = self._templateCatalog.GetAll(self._dataSource)

        self._listbox: tk.Listbox | None = None
        self._detailsText: tk.Text | None = None
        self._templateTitleVar: tk.StringVar | None = None
        self._templateDescriptionVar: tk.StringVar | None = None

        self._parametersHost: tk.Frame | None = None
        self._activeTemplate: EditorEventTemplate | None = None
        self._activeParameters: List[EditorTemplateParameter] = []

        self._filterVar: tk.StringVar | None = None

        self._refreshListsButton: ttk.Button | None = None
        self._executeButton: ttk.Button | None = None

    def Build(self, parent: tk.Frame) -> None:
        palette = Theme.Palette

        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=2)
        parent.rowconfigure(0, weight=1)

        left = tk.Frame(parent, bg=palette.surfaceDeep)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        right = tk.Frame(parent, bg=palette.surface)
        right.grid(row=0, column=1, sticky="nsew")

        # Left: search + templates list
        header = tk.Frame(left, bg=palette.surfaceDeep)
        header.pack(fill=tk.X, padx=8, pady=(8, 6))

        tk.Label(
            header,
            text=self.__Text("events.editor.templates", default="Templates"),
            bg=palette.surfaceDeep,
            fg=palette.text,
            font=("Segoe UI Semibold", 10),
        ).pack(side=tk.LEFT)

        self._filterVar = tk.StringVar(value="")
        filterEntry = tk.Entry(header, textvariable=self._filterVar, bg=palette.button, fg=palette.text, insertbackground=palette.text, relief=tk.FLAT)
        filterEntry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))
        filterEntry.bind("<KeyRelease>", lambda event: self.__RenderTemplateList(preserveSelection=True))

        listFrame = tk.Frame(left, bg=palette.surfaceDeep)
        listFrame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        scrollbar = tk.Scrollbar(listFrame, orient="vertical")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._listbox = tk.Listbox(
            listFrame,
            bg=palette.surfaceDeep,
            fg=palette.text,
            selectbackground=palette.button,
            selectforeground=palette.text,
            highlightthickness=0,
            activestyle="none",
        )
        self._listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self._listbox.yview)
        self._listbox.bind("<<ListboxSelect>>", lambda event: self.__OnTemplateSelected())

        # Right: template header + parameters + preview
        self._templateTitleVar = tk.StringVar(value="")
        self._templateDescriptionVar = tk.StringVar(value="")

        titleRow = tk.Frame(right, bg=palette.surface)
        titleRow.pack(fill=tk.X, padx=8, pady=(8, 4))

        tk.Label(titleRow, textvariable=self._templateTitleVar, bg=palette.surface, fg=palette.text, font=("Segoe UI Semibold", 11)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        actionRow = tk.Frame(right, bg=palette.surface)
        actionRow.pack(fill=tk.X, padx=8, pady=(0, 6))

        copyJsonButton = ttk.Button(actionRow, text=self.__Text("events.editor.button.copyJson", default="Copy JSON"), command=self.__CopyJson, style="Neutral.TButton")
        copyJsonButton.pack(side=tk.RIGHT)

        executeButton = ttk.Button(actionRow, text=self.__Text("events.editor.button.execute", default="Execute"), command=self.__Execute, style="Accent.TButton")
        executeButton.pack(side=tk.RIGHT, padx=(0, 8))
        self._executeButton = executeButton

        refreshListsButton = ttk.Button(
            actionRow,
            text=self.__Text("events.editor.button.refreshLists", default="Refresh Lists"),
            command=self.__RefreshLookups,
            style="Neutral.TButton",
        )
        refreshListsButton.pack(side=tk.LEFT)
        self._refreshListsButton = refreshListsButton

        tk.Label(right, textvariable=self._templateDescriptionVar, bg=palette.surface, fg=palette.textFaint, wraplength=520, justify=tk.LEFT).pack(fill=tk.X, padx=8, pady=(0, 8))

        self._parametersHost = tk.Frame(right, bg=palette.surface)
        self._parametersHost.pack(fill=tk.X, padx=0, pady=(0, 8))

        previewFrame = tk.Frame(right, bg=palette.surface)
        previewFrame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        previewHeader = tk.Frame(previewFrame, bg=palette.surface)
        previewHeader.pack(fill=tk.X)
        tk.Label(previewHeader, text=self.__Text("events.editor.preview.title", default="Generated JSON"), bg=palette.surface, fg=palette.text).pack(
            side=tk.LEFT
        )

        previewTextFrame = tk.Frame(previewFrame, bg=palette.surface)
        previewTextFrame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        previewScroll = tk.Scrollbar(previewTextFrame, orient="vertical")
        previewScroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._detailsText = tk.Text(
            previewTextFrame,
            bg=palette.button,
            fg=palette.textMuted,
            insertbackground=palette.text,
            wrap=tk.NONE,
            relief=tk.FLAT,
            yscrollcommand=previewScroll.set,
            font=("Cascadia Mono", 9),
        )
        self._detailsText.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        previewScroll.config(command=self._detailsText.yview)

        self.__RenderTemplateList(preserveSelection=False)
        self.__SelectFirstTemplate()

    def __SelectFirstTemplate(self) -> None:
        if self._listbox is None:
            return
        if self._listbox.size() <= 0:
            return
        try:
            self._listbox.selection_clear(0, tk.END)
            self._listbox.selection_set(0)
            self._listbox.activate(0)
            self._listbox.see(0)
        except Exception:
            return
        self.__OnTemplateSelected()

    def __RenderTemplateList(self, preserveSelection: bool) -> None:
        if self._listbox is None:
            return

        preservedTitle: str | None = None
        if preserveSelection:
            selected = self._listbox.curselection()
            if selected:
                try:
                    preservedTitle = str(self._listbox.get(int(selected[0])))
                except Exception:
                    preservedTitle = None

        query = ""
        if self._filterVar is not None:
            query = str(self._filterVar.get() or "").strip().lower()

        visible: List[EditorEventTemplate] = []
        for template in self._templates:
            text = f"{template.title} {template.templateId}".lower()
            if (not query) or (query in text):
                visible.append(template)

        self._listbox.delete(0, tk.END)
        for template in visible:
            self._listbox.insert(tk.END, template.title)

        if preservedTitle is not None:
            try:
                index = list(self._listbox.get(0, tk.END)).index(preservedTitle)
                self._listbox.selection_set(index)
                self._listbox.activate(index)
                self._listbox.see(index)
            except Exception:
                pass

    def __OnTemplateSelected(self) -> None:
        if self._listbox is None:
            return
        selection = self._listbox.curselection()
        if not selection:
            return

        selectedTitle = str(self._listbox.get(int(selection[0])))
        template = next((item for item in self._templates if item.title == selectedTitle), None)
        if template is None:
            return

        self._activeTemplate = template
        if self._templateTitleVar is not None:
            self._templateTitleVar.set(template.title)
        if self._templateDescriptionVar is not None:
            self._templateDescriptionVar.set(template.description)

        self.__BuildParameters(template)
        self.__RenderPreview()

    def __BuildParameters(self, template: EditorEventTemplate) -> None:
        host = self._parametersHost
        if host is None:
            return

        for parameter in self._activeParameters:
            try:
                parameter.Destroy()
            except Exception:
                pass
        self._activeParameters = []

        for child in list(host.winfo_children()):
            try:
                child.destroy()
            except Exception:
                pass

        sectionHeader = tk.Frame(host, bg=Theme.Palette.surface)
        sectionHeader.pack(fill=tk.X, padx=8, pady=(0, 6))

        endpoint = self.__GetEndpointText()
        tk.Label(
            sectionHeader,
            text=self.__Text("events.editor.parameters.endpoint", default=f"Endpoint: {endpoint}", endpoint=endpoint),
            bg=Theme.Palette.surface,
            fg=Theme.Palette.textFaint,
        ).pack(side=tk.LEFT)

        for parameter in template.BuildParameters():
            self._activeParameters.append(parameter)
            parameter.Build(host, onChanged=self.__RenderPreview)

    def __GetEndpointText(self) -> str:
        try:
            settings = self._settingsService.Get()
            host = str(getattr(settings, "rimApiHost", "localhost") or "localhost")
            port = int(getattr(settings, "rimApiPort", 0) or 0)
            return f"{host}:{port}" if port else host
        except Exception:
            return "localhost"

    def __RefreshLookups(self) -> None:
        button = self._refreshListsButton
        if button is None:
            self.__RefreshLookupsBlocking()
            return

        def warmUp() -> None:
            try:
                self._dataSource.InvalidateAll()
            except Exception:
                pass
            self._dataSource.WarmUpAll()

        BusyButtonTask(
            button,
            work=warmUp,
            onSuccess=lambda _: self.__RefreshLookupsBlocking(),
            onError=lambda error: self.__RefreshLookupsBlocking(),
            busyText="Loading...",
        ).Invoke()

    def __RefreshLookupsBlocking(self) -> None:
        if self._activeTemplate is None:
            return
        try:
            self.__BuildParameters(self._activeTemplate)
            self.__RenderPreview()
        except Exception:
            pass
        self._setStatus(self.__Text("events.editor.status.refreshedLookups", default="Refreshed lookups"))

    def __CollectValues(self) -> Dict[str, object]:
        values: Dict[str, object] = {}
        for parameter in self._activeParameters:
            try:
                values[parameter.key] = parameter.GetValue()
            except Exception:
                continue
        return values

    def __BuildDocument(self) -> Optional[Dict[str, object]]:
        template = self._activeTemplate
        if template is None:
            return None
        values = self.__CollectValues()
        try:
            return template.BuildDocument(values)
        except Exception as error:
            self._setStatus(self.__Text("events.editor.status.templateBuildFailed", default=f"Template build failed: {error}", error=str(error)))
            return None

    def __RenderPreview(self) -> None:
        if self._detailsText is None:
            return

        document = self.__BuildDocument()
        if document is None:
            self._detailsText.delete("1.0", tk.END)
            self._detailsText.insert(tk.END, self.__Text("events.editor.preview.noTemplateSelected", default="No template selected"))
            return

        try:
            rendered = json.dumps(document, indent=2, ensure_ascii=False)
        except Exception:
            rendered = str(document)

        self._detailsText.delete("1.0", tk.END)
        self._detailsText.insert(tk.END, rendered)

    def __CopyJson(self) -> None:
        document = self.__BuildDocument()
        if document is None:
            return

        root = None
        if self._detailsText is not None:
            try:
                root = self._detailsText.winfo_toplevel()
            except Exception:
                root = None
        if root is None:
            return

        try:
            rendered = json.dumps(document, indent=2, ensure_ascii=False)
        except Exception:
            rendered = str(document)

        try:
            root.clipboard_clear()
            root.clipboard_append(rendered)
            self._setStatus(self.__Text("events.editor.status.copiedJson", default="Copied JSON"))
        except Exception:
            pass

    def __Execute(self) -> None:
        document = self.__BuildDocument()
        if document is None:
            return

        try:
            definition = GameEventDefinition.FromJson(document)
        except Exception as error:
            self._setStatus(self.__Text("events.editor.status.invalidEventJson", default=f"Invalid event JSON: {error}", error=str(error)))
            return

        try:
            settings = self._settingsService.Get()
            host = str(getattr(settings, "rimApiHost", "localhost") or "localhost")
            port = int(getattr(settings, "rimApiPort", 0) or 0)
        except Exception:
            host, port = "localhost", 0

        button = self._executeButton
        if button is None:
            self.__ExecuteBlocking(host, port, definition)
            return

        BusyButtonTask(
            button,
            work=lambda: self._executor.Execute(host, port, definition),
            onSuccess=lambda results: self.__ReportExecuteResult(definition, results),
            onError=lambda error: self._setStatus(self.__Text("events.editor.status.executeFailed", default=f"Execute failed: {error}", error=str(error))),
            busyText="Executing...",
        ).Invoke()

    def __ExecuteBlocking(self, host: str, port: int, definition: GameEventDefinition) -> None:
        try:
            results = self._executor.Execute(host, port, definition)
            self.__ReportExecuteResult(definition, results)
        except Exception as error:
            self._setStatus(self.__Text("events.editor.status.executeFailed", default=f"Execute failed: {error}", error=str(error)))

    def __ReportExecuteResult(self, definition: GameEventDefinition, results: object) -> None:
        try:
            summary = "ok"
            if isinstance(results, list) and results:
                summary = str(results[0])
            self._setStatus(self.__Text("events.editor.status.executed", default=f"Executed: {definition.label} ({summary})", label=definition.label, summary=summary))
        except Exception:
            self._setStatus(self.__Text("events.editor.status.executed", default=f"Executed: {definition.label}", label=definition.label, summary=""))

    def __Text(self, key: str, default: str, **formatArgs: object) -> str:
        if self._localizer is None:
            return default
        try:
            return self._localizer.Text(key, **formatArgs)
        except Exception:
            return default
