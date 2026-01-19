from dataclasses import dataclass
from typing import Any, Dict, List

from src.game_events.templates.game_event_template_parameter import GameEventTemplateParameter
from src.game_events.templates.game_event_template_request import GameEventTemplateRequest


@dataclass(frozen=True)
class GameEventTemplateDefinition:
    templateId: str
    label: str
    cost: int
    probability: float
    tags: List[str]
    userMessage: str | None
    notificationTemplate: Any | None
    hidden: bool
    parameters: List[GameEventTemplateParameter]
    requests: List[GameEventTemplateRequest]

    @staticmethod
    def FromJson(document: Dict[str, Any]) -> "GameEventTemplateDefinition":
        if not isinstance(document, dict):
            raise ValueError("Template document must be an object")

        templateId = str(document.get("id", "") or "").strip()
        if not templateId:
            raise ValueError("Template missing required field 'id'")

        label = str(document.get("label", "") or "").strip() or templateId
        cost = int(document.get("cost", 0) or 0)
        probability = float(document.get("probability", 1.0) if document.get("probability", None) is not None else 1.0)

        rawTags = document.get("tags", [])
        tags: List[str] = []
        if isinstance(rawTags, list):
            tags = [str(value) for value in rawTags if str(value).strip()]

        rawUserMessage = document.get("userMessage", None)
        userMessage = str(rawUserMessage).strip() if rawUserMessage is not None and str(rawUserMessage).strip() else None

        rawNotification = document.get("notification", None)
        notificationTemplate: Any | None = rawNotification if isinstance(rawNotification, dict) else None

        hidden = bool(document.get("hidden", False) or False)

        rawParameters = document.get("parameters", {})
        parameters: List[GameEventTemplateParameter] = []
        if isinstance(rawParameters, dict):
            for name, value in rawParameters.items():
                if not isinstance(name, str):
                    continue
                if not isinstance(value, dict):
                    continue
                parameters.append(GameEventTemplateParameter.FromJson(name, value))

        rawRequests = document.get("requests", [])
        requests: List[GameEventTemplateRequest] = []
        if isinstance(rawRequests, list):
            for item in rawRequests:
                if not isinstance(item, dict):
                    continue
                requests.append(GameEventTemplateRequest.FromJson(item))

        return GameEventTemplateDefinition(
            templateId=templateId,
            label=label,
            cost=cost,
            probability=probability,
            tags=tags,
            userMessage=userMessage,
            notificationTemplate=notificationTemplate,
            hidden=hidden,
            parameters=parameters,
            requests=requests,
        )
