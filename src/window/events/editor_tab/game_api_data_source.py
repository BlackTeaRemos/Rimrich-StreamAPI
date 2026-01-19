from __future__ import annotations

import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.core.settings.settings_service import SettingsService
from src.window.rest_api_client import RestApiClient


class GameApiDataSource:
    def __init__(self, settingsService: SettingsService, client: RestApiClient) -> None:
        self._settingsService = settingsService
        self._client = client

        self._cache: Dict[str, Tuple[float, object]] = {}
        self._cacheSeconds: float = 10.0

    def InvalidateAll(self) -> None:
        self._cache = {}

    def WarmUpAll(self) -> None:
        """WarmUpAll prefetches common lookup lists.

        Intended to run off the UI thread so subsequent widget builds use cached results.
        """

        warmUpCalls = [
            lambda: self.GetMaps(forceRefresh=True),
            lambda: self.GetFactions(forceRefresh=True),
            lambda: self.GetPawnKinds(presentOnly=False, forceRefresh=True),
            lambda: self.GetPawnKinds(presentOnly=True, forceRefresh=True),
            lambda: self.GetRaidCatalog(forceRefresh=True),
            lambda: self.GetThingCatalog(forceRefresh=True),
            lambda: self.GetIncidentCatalog(forceRefresh=True),
            lambda: self.GetHediffCatalog(forceRefresh=True),
            lambda: self.GetPawns(forceRefresh=True),
        ]

        for warmUpCall in warmUpCalls:
            try:
                warmUpCall()
            except Exception:
                continue

    def GetMaps(self, forceRefresh: bool = False) -> List[Tuple[str, int]]:
        data = self.__GetCached("maps", lambda: self.__GetJson("/api/maps"), forceRefresh)
        return self.__ExtractMapTuples(data)

    def GetFactions(self, forceRefresh: bool = False) -> List[str]:
        data = self.__GetCached("factions", lambda: self.__GetJson("/api/factions"), forceRefresh)
        return self.__ExtractStringList(data, preferredKeys=["defName", "factionDefName", "name", "id"])

    def GetPawnKinds(self, presentOnly: bool = False, forceRefresh: bool = False) -> List[str]:
        key = f"pawnKinds:{presentOnly}"
        query = {"presentOnly": "true"} if presentOnly else {}
        data = self.__GetCached(key, lambda: self.__GetJson("/api/pawns/kinds", query=query), forceRefresh)
        return self.__ExtractStringList(data, preferredKeys=["defName", "kind", "pawnKindDefName", "name", "id"])

    def GetRaidCatalog(self, forceRefresh: bool = False) -> Dict[str, List[str]]:
        data = self.__GetCached("raidsCatalog", lambda: self.__GetJson("/api/raids/catalog"), forceRefresh)
        strategies = self.__ExtractStringList(self.__TryGetField(data, ["raidStrategies", "strategies", "strategyDefs"]), preferredKeys=["defName", "name", "id"])
        arrivals = self.__ExtractStringList(self.__TryGetField(data, ["arrivalModes", "arrivals", "arrivalModeDefs"]), preferredKeys=["defName", "name", "id"])
        factions = self.__ExtractStringList(self.__TryGetField(data, ["factions", "raidFactions"]), preferredKeys=["defName", "factionDefName", "name", "id"])
        return {
            "raidStrategyDefName": strategies,
            "arrivalModeDefName": arrivals,
            "factionDefName": factions,
        }

    def GetThingCatalog(self, techMode: str = "Range", minTechLevel: str = "", maxTechLevel: str = "", limit: int = 200, forceRefresh: bool = False) -> List[str]:
        query: Dict[str, str] = {
            "techMode": str(techMode),
            "limit": str(int(limit)),
        }
        if str(minTechLevel).strip() != "":
            query["minTechLevel"] = str(minTechLevel).strip()
        if str(maxTechLevel).strip() != "":
            query["maxTechLevel"] = str(maxTechLevel).strip()

        key = f"thingsCatalog:{query.get('techMode')}:{query.get('minTechLevel','')}:{query.get('maxTechLevel','')}:{query.get('limit')}"
        data = self.__GetCached(key, lambda: self.__GetJson("/api/things/catalog", query=query), forceRefresh)
        return self.__ExtractStringList(data, preferredKeys=["defName", "thingDefName", "name", "id"])

    def GetIncidentCatalog(self, forceRefresh: bool = False) -> List[str]:
        data = self.__GetCached("incidentsCatalog", lambda: self.__GetJson("/api/incidents/catalog"), forceRefresh)
        return self.__ExtractStringList(data, preferredKeys=["incidentDefName", "defName", "name", "id"])

    def GetHediffCatalog(self, forceRefresh: bool = False) -> List[str]:
        data = self.__GetCached("hediffsCatalog", lambda: self.__GetJson("/api/hediffs/catalog"), forceRefresh)
        return self.__ExtractStringList(data, preferredKeys=["hediffDefName", "defName", "name", "id"])

    def GetPawns(self, forceRefresh: bool = False) -> List[Tuple[str, int]]:
        data = self.__GetCached("pawns", lambda: self.__GetJson("/api/pawns"), forceRefresh)
        return self.__ExtractPawnTuples(data)

    def __GetEndpoint(self) -> Tuple[str, int]:
        try:
            settings = self._settingsService.Get()
            host = str(getattr(settings, "rimApiHost", "localhost") or "localhost").strip() or "localhost"
            port = int(getattr(settings, "rimApiPort", 0) or 0)
            return host, port
        except Exception:
            return "localhost", 0

    def __GetJson(self, path: str, query: Optional[Dict[str, str]] = None) -> object:
        host, port = self.__GetEndpoint()
        return self._client.GetJson(host, port, path, query=query or {})

    def __GetCached(self, key: str, loader: Callable[[], object], forceRefresh: bool) -> object:
        now = time.time()
        if not forceRefresh:
            cached = self._cache.get(key)
            if cached is not None:
                cachedAt, value = cached
                if (now - cachedAt) <= self._cacheSeconds:
                    return value

        value = loader()
        self._cache[key] = (now, value)
        return value

    def __TryGetField(self, parsed: object, keys: List[str]) -> object:
        if isinstance(parsed, dict):
            for key in keys:
                if key in parsed:
                    return parsed[key]
            if "data" in parsed:
                return self.__TryGetField(parsed.get("data"), keys)
        return parsed

    def __ExtractMapTuples(self, parsed: object) -> List[Tuple[str, int]]:
        items = self.__ExtractItems(parsed)
        maps: List[Tuple[str, int]] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            mapIdValue = item.get("mapId", item.get("id", item.get("index", 0)))
            try:
                mapId = int(mapIdValue)
            except Exception:
                continue
            label = str(item.get("name", item.get("label", f"Map {mapId}")) or f"Map {mapId}")
            maps.append((f"{mapId} - {label}", mapId))
        if maps:
            return maps
        return [("0", 0)]

    def __ExtractStringList(self, parsed: object, preferredKeys: List[str]) -> List[str]:
        items = self.__ExtractItems(parsed)
        if isinstance(parsed, list) and all(isinstance(value, str) for value in parsed):
            return [str(value) for value in parsed if str(value).strip()]

        values: List[str] = []
        for item in items:
            if isinstance(item, str):
                if item.strip():
                    values.append(item.strip())
                continue
            if not isinstance(item, dict):
                continue
            for key in preferredKeys:
                if key in item and str(item.get(key) or "").strip() != "":
                    values.append(str(item.get(key)).strip())
                    break

        unique = sorted({value for value in values if value.strip()})
        return unique

    def __ExtractPawnTuples(self, parsed: object) -> List[Tuple[str, int]]:
        items = self.__ExtractItems(parsed)

        pawns: List[Tuple[str, int]] = []
        for item in items:
            if not isinstance(item, dict):
                continue

            pawnIdValue = item.get("pawnId", item.get("id", item.get("thingId", 0)))
            try:
                pawnId = int(pawnIdValue)
            except Exception:
                continue

            name = str(item.get("name", "") or "").strip()
            kindDefName = str(item.get("kindDefName", "") or "").strip()
            faction = str(item.get("faction", "") or "").strip()

            labelParts: List[str] = []
            if name:
                labelParts.append(name)
            if kindDefName:
                labelParts.append(kindDefName)
            if faction:
                labelParts.append(faction)

            label = " / ".join(labelParts) if labelParts else f"Pawn {pawnId}"
            pawns.append((f"{pawnId} - {label}", pawnId))

        if pawns:
            return pawns
        return [("0", 0)]

    def __ExtractItems(self, parsed: object) -> List[object]:
        if isinstance(parsed, list):
            return list(parsed)
        if isinstance(parsed, dict):
            for key in ["items", "data", "factions", "maps", "kinds", "things"]:
                if key in parsed and isinstance(parsed[key], list):
                    return list(parsed[key])
            if "data" in parsed:
                return self.__ExtractItems(parsed.get("data"))
        return []
