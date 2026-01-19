from __future__ import annotations

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List
import tkinter as tk

from src.core.localization.localizer import Localizer
from src.game_events.game_event_executor import GameEventExecutor
from src.game_events.templates.game_event_template_instantiator import GameEventTemplateInstantiator
from src.game_events.templates.template_distribution_sampler import TemplateDistributionSampler
from src.game_events.templates.template_value_resolver import TemplateValueResolver
from src.window.events.catalog_item import CatalogItem
from src.window.events.catalog_tab import CatalogTab


class EventTestRunner:
    def __init__(self, executor: GameEventExecutor, localizer: Localizer) -> None:
        self._executor = executor
        self._localizer = localizer

    def Start(
        self,
        window: tk.Misc,
        host: str,
        port: int,
        items: List[CatalogItem],
        setStatus: Callable[[str], None],
    ) -> None:
        def setStatusFromWorker(text: str) -> None:
            try:
                window.after(0, lambda: setStatus(text))
            except Exception:
                return

        worker = threading.Thread(
            target=self.RunAllItemsAndLog,
            args=(host, port, items, setStatusFromWorker),
            name="StreamApiEventTester",
            daemon=True,
        )
        worker.start()

    def StartForVisibleCatalogItems(
        self,
        window: tk.Misc,
        host: str,
        port: int,
        catalogTab: CatalogTab,
        items: List[CatalogItem],
        setStatus: Callable[[str], None],
    ) -> None:
        indices = catalogTab.GetVisibleItemIndicesInDisplayOrder()
        if not indices:
            setStatus(self._localizer.Text("events.status.noVisibleEvents"))
            return

        itemsToRun: List[CatalogItem] = []
        for index in indices:
            if 0 <= index < len(items):
                itemsToRun.append(items[index])

        if not itemsToRun:
            setStatus(self._localizer.Text("events.status.noVisibleEvents"))
            return

        self.Start(window, host, port, itemsToRun, setStatus)

    def RunAllItemsAndLog(self, host: str, port: int, items: List[CatalogItem], setStatus: Callable[[str], None]) -> None:
        startTimestamp = datetime.now()
        launchDirectory = Path.cwd()
        logsDirectory = launchDirectory / "launch_logs"
        try:
            logsDirectory.mkdir(parents=True, exist_ok=True)
        except Exception:
            logsDirectory = launchDirectory

        logPath = logsDirectory / f"event_test_{startTimestamp.strftime('%Y%m%d_%H%M%S')}.log"

        templateInstantiator = GameEventTemplateInstantiator(TemplateDistributionSampler(), TemplateValueResolver())

        def writeLine(fileHandle: Any, text: str) -> None:
            try:
                fileHandle.write(text + "\n")
                fileHandle.flush()
            except Exception:
                return

        setStatus(self._localizer.Text("eventTest.running", count=len(items), fileName=logPath.name))

        try:
            with logPath.open("w", encoding="utf-8", newline="\n") as fileHandle:
                writeLine(fileHandle, "===== StreamAPI Event Test Run =====")
                writeLine(fileHandle, f"Started: {startTimestamp.isoformat(timespec='seconds')}")
                writeLine(fileHandle, f"Endpoint: {host}:{port}")
                writeLine(fileHandle, f"Count: {len(items)}")
                writeLine(fileHandle, "")

                for index, item in enumerate(items, start=1):
                    eventStart = time.time()

                    definitionLabel = item.DisplayText()
                    eventInfo: Dict[str, Any] = {}
                    responses: List[Dict[str, object]] = []

                    try:
                        if item.kind == "event":
                            definition = item.entry.definition
                            definitionLabel = str(definition.label)
                            eventInfo = self._BuildEventInfo(
                                kind="normal",
                                identifier=str(definition.eventId),
                                label=str(definition.label),
                                cost=int(getattr(definition, "cost", 0) or 0),
                                probability=float(getattr(definition, "probability", 0) or 0),
                                tags=list(getattr(definition, "tags", []) or []),
                                notification=getattr(definition, "notification", None),
                                sourceFile=item.FilePathString(),
                            )
                            responses = self._executor.ExecuteDetailed(host, port, definition)
                        else:
                            template = item.entry.definition
                            instantiated = templateInstantiator.Instantiate(template)
                            definitionLabel = str(template.label)
                            eventInfo = self._BuildEventInfo(
                                kind="random",
                                identifier=str(template.templateId),
                                label=str(template.label),
                                cost=int(getattr(template, "cost", 0) or 0),
                                probability=float(getattr(template, "probability", 0) or 0),
                                tags=list(getattr(template, "tags", []) or []),
                                notification=getattr(instantiated, "notification", None),
                                sourceFile=item.FilePathString(),
                            )
                            responses = self._executor.ExecuteDetailed(host, port, instantiated)
                    except Exception as error:
                        eventInfo = {
                            "type": "normal" if item.kind == "event" else "random",
                            "label": definitionLabel,
                            "file": item.FilePathString(),
                            "error": str(error),
                        }
                        responses = [{"ok": False, "status": 0, "error": str(error), "summary": str(error), "body": ""}]

                    elapsed = time.time() - eventStart
                    setStatus(self._localizer.Text("eventTest.progress", index=index, count=len(items), label=definitionLabel, seconds=elapsed))

                    writeLine(fileHandle, "=" * 72)
                    writeLine(fileHandle, f"#{index} {definitionLabel}")
                    writeLine(fileHandle, "-- EVENT --")
                    try:
                        writeLine(fileHandle, json.dumps(eventInfo, indent=2, ensure_ascii=False))
                    except Exception:
                        writeLine(fileHandle, str(eventInfo))

                    writeLine(fileHandle, "-- RESPONSE --")
                    try:
                        writeLine(fileHandle, json.dumps(responses, indent=2, ensure_ascii=False))
                    except Exception:
                        writeLine(fileHandle, str(responses))
                    writeLine(fileHandle, "")

                endTimestamp = datetime.now()
                writeLine(fileHandle, "===== DONE =====")
                writeLine(fileHandle, f"Finished: {endTimestamp.isoformat(timespec='seconds')}")

            setStatus(self._localizer.Text("eventTest.complete", path=str(logPath)))
        except Exception as error:
            setStatus(self._localizer.Text("eventTest.failed", error=str(error)))

    def _BuildEventInfo(
        self,
        kind: str,
        identifier: str,
        label: str,
        cost: int,
        probability: float,
        tags: List[str],
        notification: object,
        sourceFile: str,
    ) -> Dict[str, Any]:
        notificationInfo: Dict[str, Any] | None = None
        try:
            if notification is not None:
                notificationInfo = {
                    "delivery": getattr(notification, "delivery", None),
                    "severity": getattr(notification, "severity", None),
                    "title": getattr(notification, "title", None),
                    "message": getattr(notification, "message", None),
                    "color": getattr(notification, "color", None),
                }
        except Exception:
            notificationInfo = None

        return {
            "type": kind,
            "id": identifier,
            "label": label,
            "cost": int(cost or 0),
            "probability": float(probability or 0),
            "tags": list(tags or []),
            "notification": notificationInfo,
            "file": sourceFile,
        }
