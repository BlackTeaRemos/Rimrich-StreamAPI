from typing import Any, Dict, List

from src.game_events.game_event_definition import GameEventDefinition
from src.game_events.game_event_notification_options import GameEventNotificationOptions
from src.game_events.game_event_request import GameEventRequest
from src.game_events.templates.game_event_template_definition import GameEventTemplateDefinition
from src.game_events.templates.template_distribution_sampler import TemplateDistributionSampler
from src.game_events.templates.template_value_resolver import TemplateValueResolver


class GameEventTemplateInstantiator:
    def __init__(self, sampler: TemplateDistributionSampler, resolver: TemplateValueResolver) -> None:
        self._sampler = sampler
        self._resolver = resolver

    def Instantiate(self, template: GameEventTemplateDefinition) -> GameEventDefinition:
        values = self.__SampleValues(template)
        requests = self.__BuildRequests(template, values)

        fallbackMessage = template.userMessage or template.label
        notification: GameEventNotificationOptions | None = None
        if template.notificationTemplate is not None:
            resolvedNotification = self._resolver.Resolve(template.notificationTemplate, values)
            notificationDocument = resolvedNotification if isinstance(resolvedNotification, dict) else None
            notification = GameEventNotificationOptions.FromJson(notificationDocument, fallback_title=template.label, fallback_message=fallbackMessage)

        return GameEventDefinition(
            eventId=template.templateId,
            label=template.label,
            cost=int(template.cost),
            probability=float(template.probability),
            tags=list(template.tags),
            requests=requests,
            userMessage=template.userMessage,
            notification=notification,
            hidden=bool(template.hidden),
        )

    def __SampleValues(self, template: GameEventTemplateDefinition) -> Dict[str, Any]:
        values: Dict[str, Any] = {}
        for parameter in template.parameters:
            values[parameter.name] = self._sampler.Sample(parameter.distribution)
        return values

    def __BuildRequests(self, template: GameEventTemplateDefinition, values: Dict[str, Any]) -> List[GameEventRequest]:
        requests: List[GameEventRequest] = []
        for requestTemplate in template.requests:
            resolvedBody = self._resolver.Resolve(requestTemplate.bodyTemplate, values)
            resolvedQuery = self._resolver.Resolve(requestTemplate.queryTemplate, values)
            bodyDict: Dict[str, Any] = resolvedBody if isinstance(resolvedBody, dict) else {}
            queryDictRaw: Dict[str, Any] = resolvedQuery if isinstance(resolvedQuery, dict) else {}
            queryDict = {str(key): str(value) for key, value in queryDictRaw.items()}
            requests.append(GameEventRequest(method=requestTemplate.method, path=requestTemplate.path, payload=requestTemplate.payload, body=bodyDict, query=queryDict))
        return requests
