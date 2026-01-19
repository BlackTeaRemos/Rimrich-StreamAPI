from pathlib import Path

from src.core.app.application import Application
from src.core.localization.localizer_provider import LocalizerProvider
from src.core.events.event_bus import EventBus
from src.core.settings.settings_repository import SettingsRepository
from src.core.settings.settings_service import SettingsService
from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.game_events.game_event_executor import GameEventExecutor
from src.game_events.game_event_repository import GameEventRepository
from src.game_events.jsonc_document_loader import JsoncDocumentLoader
from src.game_events.templates.game_event_template_catalog_service import GameEventTemplateCatalogService
from src.game_events.templates.game_event_template_repository import GameEventTemplateRepository
from src.listeners.chat_event_listener import ChatEventListener
from src.listeners.chat_response_event_listener import ChatResponseEventListener
from src.listeners.overlay_event_listener import OverlayEventListener
from src.listeners.purchase_event_listener import PurchaseEventListener
from src.listeners.settings_event_listener import SettingsEventListener
from src.listeners.twitch_event_listener import TwitchEventListener
from src.listeners.twitch_status_event_listener import TwitchStatusEventListener
from src.listeners.voting_event_listener import VotingEventListener
from src.listeners.window_event_listener import WindowEventListener
from src.purchases.balance_repository import BalanceRepository
from src.purchases.balance_service import BalanceService
from src.purchases.chat_command_handler import ChatCommandHandler
from src.purchases.events_web_server import EventsWebServer
from src.purchases.purchase_service import PurchaseService
from src.purchases.silver_earning_service import SilverEarningService
from src.twitch.twitch_chat_service import TwitchChatService
from src.voting.voting_service import VotingService
from src.features.overlay.service import Service
from src.window.chat_window_service import ChatWindowService
from src.window.events_window_service import EventsWindowService
from src.window.main_window_service import MainWindowService
from src.window.rest_api_client import RestApiClient
from src.window.settings_window import SettingsWindow
from src.window.ui_thread_scheduler import UiThreadScheduler


def Bootstrap(projectRoot: Path) -> None:
    eventBus = EventBus()

    uiScheduler = UiThreadScheduler()

    settingsRepo = SettingsRepository(projectRoot / "settings.json")
    settingsService = SettingsService(settingsRepo, eventBus)

    localizerProvider = LocalizerProvider(settingsService)

    overlayService = Service(eventBus, uiScheduler, localizerProvider)
    twitchService = TwitchChatService(settingsService, eventBus)

    definitionsDirectory = projectRoot / "game_event_definitions"
    definitionsRepository = GameEventRepository(definitionsDirectory, JsoncDocumentLoader())
    definitionsCatalog = GameEventCatalogService(definitionsRepository)

    templatesDirectory = projectRoot / "game_event_templates"
    templatesRepository = GameEventTemplateRepository(templatesDirectory, JsoncDocumentLoader())
    templatesCatalog = GameEventTemplateCatalogService(templatesRepository)

    votingService = VotingService(definitionsCatalog, eventBus)

    apiClient = RestApiClient()
    eventExecutor = GameEventExecutor(apiClient)

    # Purchases system
    balancesFilePath = projectRoot / "user_balances.json"
    balanceRepository = BalanceRepository(balancesFilePath)
    balanceService = BalanceService(balanceRepository)
    silverEarningService = SilverEarningService(balanceService)
    purchaseService = PurchaseService(balanceService, definitionsCatalog, eventExecutor, settingsService)
    chatCommandHandler = ChatCommandHandler(balanceService, purchaseService)
    eventsWebServer = EventsWebServer(definitionsCatalog)

    eventsWindow = EventsWindowService(
        definitionsCatalog,
        votingService,
        eventExecutor,
        settingsService,
        apiClient,
        templateCatalogService=templatesCatalog,
        localizerProvider=localizerProvider,
        uiScheduler=uiScheduler,
    )

    chatWindow = ChatWindowService(uiScheduler, localizerProvider)
    settingsWindow = SettingsWindow(settingsService, localizerProvider)

    mainWindowService = MainWindowService(
        eventBus,
        overlayService,
        settingsWindow,
        settingsService,
        twitchService,
        chatWindow,
        eventsWindow,
        balanceService,
        uiScheduler,
        localizerProvider,
    )

    windowListener = WindowEventListener(eventBus, mainWindowService)
    overlayListener = OverlayEventListener(eventBus, overlayService, mainWindowService, settingsService)
    settingsListener = SettingsEventListener(eventBus, overlayService, mainWindowService)
    twitchListener = TwitchEventListener(eventBus, twitchService, settingsService)
    chatListener = ChatEventListener(eventBus, chatWindow)
    votingListener = VotingEventListener(eventBus, votingService)
    twitchStatusListener = TwitchStatusEventListener(eventBus, mainWindowService, chatWindow)

    # Purchase system listeners
    purchaseListener = PurchaseEventListener(eventBus, balanceService, silverEarningService, chatCommandHandler)
    chatResponseListener = ChatResponseEventListener(eventBus, twitchService)

    # Start web server if purchases enabled
    currentSettings = settingsService.Get()
    if currentSettings.purchasesEnabled:
        eventsWebServer.Start(currentSettings.purchasesWebPort)

    application = Application(
        eventBus,
        [windowListener, overlayListener, settingsListener, twitchListener, chatListener, votingListener, twitchStatusListener, purchaseListener, chatResponseListener],
        bootstrap=settingsService.PublishCurrent,
    )
    application.Run()
