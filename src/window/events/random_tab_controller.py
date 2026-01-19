from __future__ import annotations

import tkinter as tk
from typing import Callable

from src.core.settings.settings_service import SettingsService
from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.game_events.game_event_executor import GameEventExecutor
from src.game_events.templates.game_event_template_catalog_service import GameEventTemplateCatalogService
from src.game_events.templates.game_event_template_instantiator import GameEventTemplateInstantiator
from src.voting.voting_service import VotingService
from src.window.events.random_tab.enabled_events_list_controller import EnabledEventsListController
from src.window.events.random_tab.tags_panel_controller import TagsPanelController
from src.window.events.random_tab.vote_controls_controller import VoteControlsController
from src.window.events.random_tab.voting_loop_controller import VotingLoopController
from src.window.theme import Theme
from src.core.localization.localizer import Localizer


class RandomTabController:
    def __init__(
        self,
        catalogService: GameEventCatalogService,
        votingService: VotingService,
        executor: GameEventExecutor,
        templateCatalogService: GameEventTemplateCatalogService | None,
        templateInstantiator: GameEventTemplateInstantiator,
        settingsService: SettingsService,
        setStatus: Callable[[str], None],
        localizer: Localizer | None = None,
    ) -> None:
        self._catalogService = catalogService
        self._votingService = votingService
        self._executor = executor
        self._templateCatalogService = templateCatalogService
        self._templateInstantiator = templateInstantiator
        self._settingsService = settingsService
        self._setStatus = setStatus
        self._localizer = localizer

        self._window: tk.Toplevel | None = None
        self._endpointLabelVar: tk.StringVar | None = None
        self._voteControls: VoteControlsController | None = None
        self._votingLoop: VotingLoopController | None = None

        self._tagsPanel = TagsPanelController(self._catalogService, self._templateCatalogService, self.__OnTagsSelectionChanged, localizer=self._localizer)
        self._enabledEvents = EnabledEventsListController(
            self._catalogService,
            self._templateCatalogService,
            self._tagsPanel.GetSelectedTags,
            localizer=self._localizer,
        )

    def Build(self, parent: tk.Frame, window: tk.Toplevel) -> None:
        self._window = window

        self._voteControls = VoteControlsController(self.Toggle, defaultDurationSeconds=30, localizer=self._localizer)
        self._votingLoop = VotingLoopController(
            catalogService=self._catalogService,
            templateCatalogService=self._templateCatalogService,
            enabledEvents=self._enabledEvents,
            votingService=self._votingService,
            executor=self._executor,
            templateInstantiator=self._templateInstantiator,
            getHost=self.__GetRimApiHost,
            getPort=self.__GetRimApiPort,
            getDurationSeconds=self._voteControls.GetDurationSeconds,
            setStatus=self._setStatus,
            setRunningUi=self._voteControls.SetRunning,
            updateTimerUi=self._voteControls.UpdateTimer,
            localizer=self._localizer,
        )
        self._votingLoop.AttachWindow(window)

        palette = Theme.Palette

        endpointRow = tk.Frame(parent, bg=palette.surface)
        endpointRow.pack(fill=tk.X, padx=0, pady=(10, 8))

        tk.Label(
            endpointRow,
            text=self.__Text("events.random.endpoint.label", default="RimWorld endpoint:"),
            bg=palette.surface,
            fg=palette.textMuted,
        ).pack(side=tk.LEFT)
        self._endpointLabelVar = tk.StringVar(value=self.__FormatEndpoint())
        tk.Label(endpointRow, textvariable=self._endpointLabelVar, bg=palette.surface, fg=palette.text).pack(side=tk.LEFT, padx=(6, 0))
        tk.Label(
            endpointRow,
            text=self.__Text("events.random.endpoint.help", default="(configure in Settings)"),
            bg=palette.surface,
            fg=palette.textFaint,
        ).pack(side=tk.LEFT, padx=(6, 0))

        controls = tk.Frame(parent, bg=palette.surface)
        controls.pack(fill=tk.X, padx=0, pady=(0, 8))

        if self._voteControls is not None:
            self._voteControls.Build(controls)

        tagsFrame = tk.Frame(parent, bg=palette.surfaceDeep)
        tagsFrame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 8))

        headerRow = tk.Frame(tagsFrame, bg=palette.surfaceDeep)
        headerRow.pack(fill=tk.X, padx=8, pady=(8, 4))
        tk.Label(
            headerRow,
            text=self.__Text("events.random.header.tags", default="Tags"),
            bg=palette.surfaceDeep,
            fg=palette.text,
            anchor="w",
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(
            headerRow,
            text=self.__Text("events.random.header.enabled", default="Enabled events"),
            bg=palette.surfaceDeep,
            fg=palette.text,
            anchor="w",
        ).pack(side=tk.RIGHT)

        contentRow = tk.Frame(tagsFrame, bg=palette.surfaceDeep)
        contentRow.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        tagsPanel = tk.Frame(contentRow, bg=palette.surfaceDeep)
        tagsPanel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._tagsPanel.Build(tagsPanel)

        enabledPanel = tk.Frame(contentRow, bg=palette.surfaceDeep)
        enabledPanel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(10, 0))

        self._enabledEvents.Build(enabledPanel)

        self.ReloadTags()

    def __Text(self, key: str, default: str, **formatArgs: object) -> str:
        if self._localizer is None:
            return default
        try:
            return self._localizer.Text(key, **formatArgs)
        except Exception:
            return default

    def Close(self) -> None:
        if self._votingLoop is not None:
            try:
                self._votingLoop.Close()
            except Exception:
                pass
        self._window = None
        self._endpointLabelVar = None
        self._tagsPanel.Close()
        self._enabledEvents.Close()
        if self._voteControls is not None:
            self._voteControls.Close()
        self._voteControls = None
        self._votingLoop = None

    def __GetRimApiHost(self) -> str:
        try:
            host = str(getattr(self._settingsService.Get(), "rimApiHost", "localhost") or "").strip()
            return host if host else "localhost"
        except Exception:
            return "localhost"

    def __GetRimApiPort(self) -> int:
        try:
            port = int(getattr(self._settingsService.Get(), "rimApiPort", 0) or 0)
            if 0 < port <= 65535:
                return port
        except Exception:
            pass
        return 8765

    def __FormatEndpoint(self) -> str:
        return f"{self.__GetRimApiHost()}:{self.__GetRimApiPort()}"

    def ReloadTags(self) -> None:
        self._tagsPanel.ReloadTags()

    def __OnTagsSelectionChanged(self) -> None:
        self._enabledEvents.UpdateEnabledEvents()

    def Toggle(self) -> None:
        if self._votingLoop is not None:
            self._votingLoop.Toggle()

    def Start(self) -> None:
        if self._votingLoop is not None:
            self._votingLoop.Start()

    def Stop(self) -> None:
        if self._votingLoop is not None:
            self._votingLoop.Stop()
