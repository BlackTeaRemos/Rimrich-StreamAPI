from typing import List, Optional

from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.game_events.game_event_definition import GameEventDefinition
from src.game_events.game_event_executor import GameEventExecutor
from src.core.settings.settings_service import SettingsService
from src.purchases.interfaces.balance_service_interface import BalanceServiceInterface
from src.purchases.interfaces.purchase_service_interface import PurchaseServiceInterface
from src.purchases.purchase_result import PurchaseResult


class PurchaseService(PurchaseServiceInterface):
    """Processes event purchases by deducting silver and triggering game events."""

    def __init__(
        self,
        balanceService: BalanceServiceInterface,
        catalogService: GameEventCatalogService,
        eventExecutor: GameEventExecutor,
        settingsService: SettingsService,
    ) -> None:
        self._balanceService = balanceService
        self._catalogService = catalogService
        self._eventExecutor = eventExecutor
        self._settingsService = settingsService

    def AttemptPurchase(self, username: str, eventIdentifier: str) -> PurchaseResult:
        """Attempt to purchase and trigger an event.

        Args:
            username: The chat username making the purchase.
            eventIdentifier: The event ID or label to purchase.

        Returns:
            PurchaseResult: Result containing success/failure and message.
        """
        eventDefinition = self._FindEvent(eventIdentifier)
        if eventDefinition is None:
            return PurchaseResult.EventNotFound(eventIdentifier)

        cost = eventDefinition.cost
        currentBalance = self._balanceService.GetBalance(username)

        if currentBalance < cost:
            return PurchaseResult.InsufficientFunds(eventDefinition.label, cost, currentBalance)

        deductionSucceeded = self._balanceService.DeductSilver(username, cost)
        if not deductionSucceeded:
            return PurchaseResult.InsufficientFunds(eventDefinition.label, cost, currentBalance)

        executionResult = self._ExecuteEvent(eventDefinition)
        if not executionResult.success:
            self._balanceService.AddSilver(username, cost)
            return executionResult

        newBalance = self._balanceService.GetBalance(username)
        self._balanceService.Persist()

        return PurchaseResult.Success(eventDefinition.label, cost, newBalance)

    def _FindEvent(self, eventIdentifier: str) -> Optional[GameEventDefinition]:
        """Find an event by ID or label (case-insensitive)."""
        normalizedIdentifier = eventIdentifier.strip().lower()
        allEvents = self._catalogService.GetAll()

        for eventDefinition in allEvents:
            if eventDefinition.eventId.lower() == normalizedIdentifier:
                return eventDefinition

        for eventDefinition in allEvents:
            if eventDefinition.label.lower() == normalizedIdentifier:
                return eventDefinition

        return None

    def _ExecuteEvent(self, eventDefinition: GameEventDefinition) -> PurchaseResult:
        """Execute the game event via REST API."""
        try:
            settings = self._settingsService.Get()
            host = settings.rimApiHost
            port = settings.rimApiPort

            results = self._eventExecutor.Execute(host, port, eventDefinition)
            
            hasError = any("error" in str(result).lower() or "failed" in str(result).lower() for result in results)
            if hasError:
                errorMessage = "; ".join(results)
                return PurchaseResult.ExecutionFailed(eventDefinition.eventId, errorMessage)

            return PurchaseResult(
                success=True,
                message="Event executed",
                eventId=eventDefinition.eventId,
                cost=eventDefinition.cost,
                newBalance=0,
            )
        except Exception as error:
            return PurchaseResult.ExecutionFailed(eventDefinition.eventId, str(error))

    def GetPurchasableEvents(self) -> List[GameEventDefinition]:
        """Get all events that can be purchased (have cost > 0 and not hidden)."""
        allEvents = self._catalogService.GetAll()
        return [
            eventDefinition
            for eventDefinition in allEvents
            if eventDefinition.cost > 0 and not eventDefinition.hidden
        ]
