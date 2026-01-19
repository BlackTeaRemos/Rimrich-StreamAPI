from src.core.events.event import Event


class AppActionEvent(Event):
    """
    AppActionEvent stores the name of a pressed action button

    Args:
        actionName (str): label describing the action example "Action One"

    Returns:
        AppActionEvent: initialized action event example AppActionEvent("Action One")
    """

    def __init__(self, actionName: str) -> None:
        super().__init__("app_action")
        self.actionName = actionName  # name of the action button
