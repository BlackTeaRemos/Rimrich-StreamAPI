class AppSettings:
    """AppSettings holds user configuration."""

    def __init__(
        self,
        borderless: bool = False,
        twitchToken: str = "",
        twitchNick: str = "",
        twitchChannel: str = "",
        chromaEnabled: bool = False,
        chromaVoterCount: int = 0,
        rimApiHost: str = "localhost",
        rimApiPort: int = 0,
        uiLanguage: str = "en",
        purchasesEnabled: bool = True,
        purchasesWebPort: int = 8080,
    ) -> None:
        self.borderless = borderless  # borderless overlay toggle
        self.twitchToken = twitchToken  # oauth token for twitch chat
        self.twitchNick = twitchNick  # username for bot
        self.twitchChannel = twitchChannel  # channel to join
        self.chromaEnabled = chromaEnabled  # chroma key background toggle
        self.chromaVoterCount = chromaVoterCount  # recent voters to show
        self.rimApiHost = rimApiHost  # rimworld api host
        self.rimApiPort = rimApiPort  # rimworld api port
        self.uiLanguage = uiLanguage  # UI language code (e.g. 'en')
        self.purchasesEnabled = purchasesEnabled  # enable chat purchases system
        self.purchasesWebPort = purchasesWebPort  # port for events web server
