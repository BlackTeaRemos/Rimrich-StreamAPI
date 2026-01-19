from typing import Any, Dict, List, Optional

from src.game_events.game_event_request import GameEventRequest
from src.game_events.game_event_notification_options import GameEventNotificationOptions


class GameEventDefinition:
    def __init__(
        self,
        eventId: str,
        label: str,
        cost: int = 0,
        probability: float = 1.0,
        tags: Optional[List[str]] = None,
        requests: Optional[List[GameEventRequest]] = None,
        userMessage: Optional[str] = None,
        notification: Optional[GameEventNotificationOptions] = None,
        hidden: bool = False,
    ) -> None:
        self.eventId = eventId
        self.label = label
        self.cost = int(cost or 0)
        self.probability = float(probability if probability is not None else 1.0)
        self.tags = tags or []
        self.requests = requests or []
        self.userMessage = str(userMessage).strip() if userMessage is not None and str(userMessage).strip() else None
        fallbackMessage = self.userMessage or self.label
        self.notification = notification or GameEventNotificationOptions.Default(fallback_title=self.label, fallback_message=fallbackMessage)
        self.hidden = bool(hidden)

    @staticmethod
    def FromJson(document: Dict[str, Any]) -> "GameEventDefinition":
        eventId = str(document.get("id", "")).strip()
        label = str(document.get("label", "")).strip() or eventId
        if not eventId:
            raise ValueError("Event definition missing required field 'id'")

        cost = int(document.get("cost", 0) or 0)
        probability = float(document.get("probability", 1.0) if document.get("probability", None) is not None else 1.0)

        rawTags = document.get("tags", [])
        tags: List[str] = []
        if isinstance(rawTags, list):
            tags = [str(value) for value in rawTags if str(value).strip()]

        rawUserMessage = document.get("userMessage", None)
        userMessage = str(rawUserMessage).strip() if rawUserMessage is not None and str(rawUserMessage).strip() else None
        hidden = bool(document.get("hidden", False) or False)

        rawNotification = document.get("notification", None)
        fallbackMessage = userMessage or label
        notification = GameEventNotificationOptions.FromJson(rawNotification, fallback_title=label, fallback_message=fallbackMessage)

        rawRequests = document.get("requests", [])
        requests: List[GameEventRequest] = []
        if isinstance(rawRequests, list):
            for item in rawRequests:
                if not isinstance(item, dict):
                    continue
                method = str(item.get("method", "POST"))
                path = str(item.get("path", "/"))
                payload = str(item.get("payload", "json"))
                body = item.get("body", {})
                query = item.get("query", {})
                if body is not None and not isinstance(body, dict):
                    body = {}
                if query is not None and not isinstance(query, dict):
                    query = {}
                requests.append(GameEventRequest(method=method, path=path, payload=payload, body=body, query={str(key): str(value) for key, value in dict(query).items()}))

        return GameEventDefinition(
            eventId=eventId,
            label=label,
            cost=cost,
            probability=probability,
            tags=tags,
            requests=requests,
            userMessage=userMessage,
            notification=notification,
            hidden=hidden,
        )
