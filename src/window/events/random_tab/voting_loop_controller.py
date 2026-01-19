from __future__ import annotations

import random
import tkinter as tk
from typing import Callable, List

from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.game_events.game_event_definition import GameEventDefinition
from src.game_events.game_event_executor import GameEventExecutor
from src.game_events.templates.game_event_template_catalog_service import GameEventTemplateCatalogService
from src.game_events.templates.game_event_template_instantiator import GameEventTemplateInstantiator
from src.voting.voting_service import VotingService
from src.window.events.random_tab.enabled_events_list_controller import EnabledEventsListController
from src.core.localization.localizer import Localizer


class VotingLoopController:
    def __init__(
        self,
        catalogService: GameEventCatalogService,
        templateCatalogService: GameEventTemplateCatalogService | None,
        enabledEvents: EnabledEventsListController,
        votingService: VotingService,
        executor: GameEventExecutor,
        templateInstantiator: GameEventTemplateInstantiator,
        getHost: Callable[[], str],
        getPort: Callable[[], int],
        getDurationSeconds: Callable[[], int],
        setStatus: Callable[[str], None],
        setRunningUi: Callable[[bool], None],
        updateTimerUi: Callable[[int], None],
        localizer: Localizer | None = None,
    ) -> None:
        self._catalogService = catalogService
        self._templateCatalogService = templateCatalogService
        self._enabledEvents = enabledEvents
        self._votingService = votingService
        self._executor = executor
        self._templateInstantiator = templateInstantiator

        self._getHost = getHost
        self._getPort = getPort
        self._getDurationSeconds = getDurationSeconds
        self._setStatus = setStatus
        self._setRunningUi = setRunningUi
        self._updateTimerUi = updateTimerUi
        self._localizer = localizer

        self._window: tk.Toplevel | None = None
        self._running = False
        self._countdownId: str | None = None
        self._remainingSeconds: int = 0

    def AttachWindow(self, window: tk.Toplevel) -> None:
        self._window = window

    def Close(self) -> None:
        try:
            self.Stop()
        except Exception:
            pass
        self._window = None

    def Toggle(self) -> None:
        if self._running:
            self.Stop()
        else:
            self.Start()

    def Start(self) -> None:
        self._running = True
        self._setRunningUi(True)

        self._remainingSeconds = self.__GetSafeDurationSeconds()
        self._setStatus(self.__Text("events.random.status.votingStarted", default="Voting started"))

        self.__StartRound()
        self.__Tick()

    def Stop(self) -> None:
        self._running = False
        self.__CancelCountdown()
        try:
            self._votingService.StopPoll()
        except Exception:
            pass
        self._setRunningUi(False)
        self._updateTimerUi(0)
        self._setStatus(self.__Text("events.random.status.stopped", default="Stopped"))

    def __StartRound(self) -> None:
        try:
            self._catalogService.Reload()
        except Exception:
            pass
        if self._templateCatalogService is not None:
            try:
                self._templateCatalogService.Reload()
            except Exception:
                pass

        definitions, templates = self._enabledEvents.GetEnabledDefinitionsAndTemplates()
        pool = list(definitions)
        for template in templates:
            try:
                pool.append(self._templateInstantiator.Instantiate(template))
            except Exception:
                continue

        if not pool:
            self._votingService.StartPollWithDefinitions([])
            self._setStatus(self.__Text("events.random.status.noEnabled", default="No enabled events (check tags)"))
            return

        chosen = self.__PickWeightedUnique(pool, 4)
        self._votingService.StartPollWithDefinitions(chosen)
        self._setStatus(self.__Text("events.random.status.newRound", default="New round started"))

    def __Tick(self) -> None:
        self.__CancelCountdown()
        if not self._running:
            return
        if self._window is None or not self._window.winfo_exists():
            self.Stop()
            return

        self._updateTimerUi(self._remainingSeconds)
        if self._remainingSeconds <= 0:
            self.__ResolveAndExecuteWinner()
            self._remainingSeconds = self.__GetSafeDurationSeconds()
            self.__StartRound()
            self._countdownId = self._window.after(0, self.__Tick)
            return

        self._remainingSeconds -= 1
        self._countdownId = self._window.after(1000, self.__Tick)

    def __GetSafeDurationSeconds(self) -> int:
        try:
            value = int(self._getDurationSeconds() or 0)
            return max(1, value)
        except Exception:
            return 30

    def __ResolveAndExecuteWinner(self) -> None:
        winnerIndex = self._votingService.GetWinnerIndex()
        definitions = self._votingService.GetActiveDefinitions()
        if winnerIndex < 0 or winnerIndex >= len(definitions):
            self._setStatus(self.__Text("events.random.status.noWinner", default="No winner (no votes)"))
            return

        winner = definitions[winnerIndex]
        try:
            results = self._executor.Execute(self._getHost(), self._getPort(), winner)
            summary = results[0] if results else "ok"
            display = winner.label
            try:
                if winner.userMessage is not None and str(winner.userMessage).strip() != "":
                    display = str(winner.userMessage).strip()
            except Exception:
                display = winner.label
            self._setStatus(self.__Text("events.random.status.executed", default=f"Executed: {display} ({summary})", display=display, summary=summary))
        except Exception as error:
            self._setStatus(self.__Text("events.random.status.executionFailed", default=f"Execution failed: {error}", error=str(error)))

    def __Text(self, key: str, default: str, **formatArgs: object) -> str:
        if self._localizer is None:
            return default
        try:
            return self._localizer.Text(key, **formatArgs)
        except Exception:
            return default

    def __PickWeightedUnique(self, pool: List[GameEventDefinition], count: int) -> List[GameEventDefinition]:
        remaining = list(pool)
        chosen: List[GameEventDefinition] = []

        while remaining and len(chosen) < count:
            weights = [max(0.0, float(item.probability)) for item in remaining]
            if all(weight == 0.0 for weight in weights):
                selection = random.choice(remaining)
            else:
                selection = random.choices(remaining, weights=weights, k=1)[0]
            chosen.append(selection)
            remaining = [item for item in remaining if item.eventId != selection.eventId]

        return chosen

    def __CancelCountdown(self) -> None:
        if self._window is None:
            return
        if self._countdownId is not None:
            try:
                self._window.after_cancel(self._countdownId)
            except Exception:
                pass
            self._countdownId = None
