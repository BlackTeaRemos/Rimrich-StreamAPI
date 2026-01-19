from typing import Dict, List, Optional

from src.game_events.game_event_definition import GameEventDefinition
from src.game_events.game_event_request import GameEventRequest
from src.window.rest_api_client import RestApiClient


class GameEventExecutor:
    def __init__(self, client: RestApiClient) -> None:
        self._client = client

    def Execute(self, host: str, port: int, definition: GameEventDefinition) -> List[str]:
        results: List[str] = []
        notificationHeaders = definition.notification.BuildHeaders()
        hasAppliedNotificationHeaders = False

        for request in definition.requests:
            headersToApply: Optional[Dict[str, str]] = None
            if not hasAppliedNotificationHeaders:
                headersToApply = notificationHeaders
                hasAppliedNotificationHeaders = True

            results.append(self.__ExecuteRequest(host, port, request, headers=headersToApply))
        return results

    def ExecuteDetailed(self, host: str, port: int, definition: GameEventDefinition) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        notificationHeaders = definition.notification.BuildHeaders()
        hasAppliedNotificationHeaders = False

        for request in definition.requests:
            headersToApply: Optional[Dict[str, str]] = None
            if not hasAppliedNotificationHeaders:
                headersToApply = notificationHeaders
                hasAppliedNotificationHeaders = True

            results.append(self.__ExecuteRequestDetailed(host, port, request, headers=headersToApply))
        return results

    def __ExecuteRequest(self, host: str, port: int, request: GameEventRequest, headers: Optional[Dict[str, str]]) -> str:
        if request.payload == "query":
            action = {"method": request.method, "path": request.path, "payload": "query"}
            return self._client.Execute(host, port, action, dict(request.query), headers=headers)

        params = {str(key): str(value) for key, value in dict(request.body).items()}
        action = {"method": request.method, "path": request.path, "payload": "json"}
        return self._client.Execute(host, port, action, params, headers=headers)

    def __ExecuteRequestDetailed(self, host: str, port: int, request: GameEventRequest, headers: Optional[Dict[str, str]]) -> Dict[str, object]:
        if request.payload == "query":
            action = {"method": request.method, "path": request.path, "payload": "query"}
            return self._client.ExecuteDetailed(host, port, action, dict(request.query), headers=headers)

        params = {str(key): str(value) for key, value in dict(request.body).items()}
        action = {"method": request.method, "path": request.path, "payload": "json"}
        return self._client.ExecuteDetailed(host, port, action, params, headers=headers)
