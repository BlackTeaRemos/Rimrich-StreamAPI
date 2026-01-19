from __future__ import annotations

import threading
import tkinter as tk
from typing import List

from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.game_events.game_event_executor import GameEventExecutor
from src.game_events.templates.game_event_template_catalog_service import GameEventTemplateCatalogService
from src.game_events.templates.game_event_template_instantiator import GameEventTemplateInstantiator
from src.game_events.templates.template_distribution_sampler import TemplateDistributionSampler
from src.game_events.templates.template_value_resolver import TemplateValueResolver
from src.voting.voting_service import VotingService
from src.core.settings.settings_service import SettingsService
from src.core.localization.localizer_provider import LocalizerProvider
from src.window.events.events_catalog_actions import EventsCatalogActions
from src.window.events.events_catalog_loader import EventsCatalogLoader
from src.window.events.catalog_item import CatalogItem
from src.window.events.catalog_tab import CatalogTab
from src.window.events.editor_tab.editor_tab import EditorTab
from src.window.events.event_test_runner import EventTestRunner
from src.window.events.events_window_view import EventsWindowView
from src.window.events.events_window_state import EventsWindowState
from src.window.events.events_tab_selector import EventsTabSelector
from src.window.events.rim_api_endpoint_provider import RimApiEndpointProvider
from src.window.events.random_tab_controller import RandomTabController
from src.window.events.protection_status_controller import ProtectionStatusController
from src.window.rest_api_client import RestApiClient
from src.window.ui_thread_scheduler import UiThreadScheduler
from src.window.busy_button_overlay import BusyButtonOverlay


class EventsWindowService:
    def __init__(
        self,
        catalogService: GameEventCatalogService,
        votingService: VotingService,
        executor: GameEventExecutor,
        settingsService: SettingsService,
        apiClient: RestApiClient,
        localizerProvider: LocalizerProvider,
        uiScheduler: UiThreadScheduler | None = None,
        templateCatalogService: GameEventTemplateCatalogService | None = None,
    ) -> None:
        self._localizerProvider = localizerProvider
        self._localizer = self._localizerProvider.Get()

        self._uiScheduler = uiScheduler

        self._endpointProvider = RimApiEndpointProvider(settingsService)

        self._windowState = EventsWindowState()
        self._protectionStatus = ProtectionStatusController(apiClient, self._endpointProvider.GetEndpoint, self._localizer)
        self._items: List[CatalogItem] = []

        self._testRunner = EventTestRunner(executor, self._localizer)
        self._view = EventsWindowView()
        self._tabSelector = EventsTabSelector()
        self._catalogLoader = EventsCatalogLoader(catalogService, templateCatalogService)
        self._catalogActions: EventsCatalogActions | None = None

        self._catalogTab = CatalogTab(self.__OnSelectionChanged, onTestAllRequested=self.__StartTestAllRun, localizer=self._localizer)
        self._catalogActions = EventsCatalogActions(self._catalogTab, self.__GetItems, self.__SetStatus, self._localizer)

        self._editorTab = EditorTab(settingsService, executor, apiClient, self.__SetStatus, localizer=self._localizer)

        templateInstantiator = GameEventTemplateInstantiator(TemplateDistributionSampler(), TemplateValueResolver())
        self._randomTab = RandomTabController(
            catalogService,
            votingService,
            executor,
            templateCatalogService,
            templateInstantiator,
            settingsService,
            self.__SetStatus,
            localizer=self._localizer,
        )

        self._reloadOverlay: BusyButtonOverlay | None = None

    def ShowWindow(self, parent: tk.Tk, initialTab: str | None = None) -> None:
        if self._windowState.IsOpen():
            self._windowState.Lift()
            self._tabSelector.Select(
                self._windowState.tabs,
                self._windowState.catalogTabFrame,
                self._windowState.randomTabFrame,
                self._windowState.editorTabFrame,
                initialTab,
            )
            return

        window, tabs, catalogTabFrame, randomTabFrame, editorTabFrame, statusVar, reloadButton, openButton = self._view.Build(
            parent,
            localizer=self._localizer,
            onReloadRequested=self.__HandleReload,
            onOpenFileRequested=self.__HandleOpenFile,
            onCloseRequested=self.__HandleClose,
            buildProtectionLabel=self._protectionStatus.Build,
        )
        self._windowState.Assign(window, tabs, catalogTabFrame, randomTabFrame, editorTabFrame, statusVar, reloadButton, openButton)

        self._catalogTab.Build(self._windowState.catalogTabFrame)
        self._randomTab.Build(self._windowState.randomTabFrame, self._windowState.window)
        self._editorTab.Build(self._windowState.editorTabFrame)

        self.__ReloadAndRender()
        self._tabSelector.Select(
            self._windowState.tabs,
            self._windowState.catalogTabFrame,
            self._windowState.randomTabFrame,
            self._windowState.editorTabFrame,
            initialTab,
        )
        self._protectionStatus.Start(self._windowState.window)

    def __HandleClose(self) -> None:
        try:
            self._protectionStatus.Stop()
        except Exception:
            pass

        try:
            self._randomTab.Close()
        except Exception:
            pass

        self._windowState.Destroy()
        self._items = []
        self._reloadOverlay = None

    def __HandleReload(self) -> None:
        self.__ReloadAndRender()

    def __StartTestAllRun(self) -> None:
        window = self._windowState.window
        if window is None:
            return

        host, port = self._endpointProvider.GetEndpoint()
        self._testRunner.StartForVisibleCatalogItems(window, host, port, self._catalogTab, self._items, self.__SetStatus)

    def __ReloadAndRender(self) -> None:
        if self._uiScheduler is None:
            self.__ReloadAndRenderBlocking()
            return

        window = self._windowState.window
        if window is None:
            return

        self.__SetBusy(True)
        self.__SetStatus("Loading events...")

        def worker() -> None:
            try:
                merged, normalCount, randomCount = self._catalogLoader.Reload()

                def applyResults() -> None:
                    self._items = merged

                    self._catalogTab.SetItems(self._items)
                    if self._items:
                        self._catalogTab.SelectFirst()
                        self.__OnSelectionChanged()
                    else:
                        self._catalogTab.ClearDetails(self._localizer.Text("events.details.noEventsLoaded"))

                    try:
                        self._randomTab.ReloadTags()
                    except Exception:
                        pass

                    self.__SetBusy(False)
                    self.__SetStatus(self._localizer.Text("events.status.loaded", normalCount=normalCount, randomCount=randomCount))

                self._uiScheduler.Post(applyResults)
            except Exception as error:
                def reportError() -> None:
                    self.__SetBusy(False)
                    self.__SetStatus(self._localizer.Text("events.status.reloadFailed", error=str(error)))

                self._uiScheduler.Post(reportError)

        threading.Thread(target=worker, name="EventsReload", daemon=True).start()

    def __ReloadAndRenderBlocking(self) -> None:
        try:
            merged, normalCount, randomCount = self._catalogLoader.Reload()
            self._items = merged

            self._catalogTab.SetItems(self._items)
            if self._items:
                self._catalogTab.SelectFirst()
                self.__OnSelectionChanged()
            else:
                self._catalogTab.ClearDetails(self._localizer.Text("events.details.noEventsLoaded"))

            self._randomTab.ReloadTags()
            self.__SetStatus(self._localizer.Text("events.status.loaded", normalCount=normalCount, randomCount=randomCount))
        except Exception as error:
            self.__SetStatus(self._localizer.Text("events.status.reloadFailed", error=str(error)))

    def __SetBusy(self, isBusy: bool) -> None:
        reloadButton = self._windowState.reloadButton
        openButton = self._windowState.openButton

        if reloadButton is not None and self._reloadOverlay is None:
            try:
                self._reloadOverlay = BusyButtonOverlay(reloadButton)
            except Exception:
                self._reloadOverlay = None

        if isBusy:
            if self._reloadOverlay is not None:
                try:
                    self._reloadOverlay.Start()
                except Exception:
                    pass

            for button in [reloadButton, openButton]:
                if button is None:
                    continue
                try:
                    button.configure(state=tk.DISABLED)
                except Exception:
                    pass
            if reloadButton is not None:
                try:
                    reloadButton.configure(text="Loading...")
                except Exception:
                    pass
            return

        if self._reloadOverlay is not None:
            try:
                self._reloadOverlay.Stop()
            except Exception:
                pass

        for button in [reloadButton, openButton]:
            if button is None:
                continue
            try:
                button.configure(state=tk.NORMAL)
            except Exception:
                pass
        if reloadButton is not None:
            try:
                reloadButton.configure(text=self._localizer.Text("events.button.reload"))
            except Exception:
                pass

    def __OnSelectionChanged(self) -> None:
        actions = self._catalogActions
        if actions is None:
            return
        actions.HandleSelectionChanged()

    def __HandleOpenFile(self) -> None:
        actions = self._catalogActions
        if actions is None:
            return
        actions.HandleOpenFile()

    def __GetItems(self) -> List[CatalogItem]:
        return self._items

    def __SetStatus(self, text: str) -> None:
        statusVar = self._windowState.statusVar
        if statusVar is None:
            return
        statusVar.set(text)
