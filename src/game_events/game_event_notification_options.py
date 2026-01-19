from typing import Any, Dict, Optional


class GameEventNotificationOptions:
    def __init__(
        self,
        delivery: str,
        severity: str,
        title: Optional[str],
        message: Optional[str],
        color: Optional[str] = None,
    ) -> None:
        self.delivery = str(delivery or "message").strip() or "message"
        self.severity = str(severity or "info").strip() or "info"
        self.title = str(title).strip() if title is not None and str(title).strip() else None
        self.message = str(message).strip() if message is not None and str(message).strip() else None
        self.color = str(color).strip() if color is not None and str(color).strip() else None

    @staticmethod
    def Default(fallback_title: str, fallback_message: str) -> "GameEventNotificationOptions":
        return GameEventNotificationOptions(
            delivery="message",
            severity="info",
            title=fallback_title,
            message=fallback_message,
            color=None,
        )

    @staticmethod
    def FromJson(raw: Any, fallback_title: str, fallback_message: str) -> "GameEventNotificationOptions":
        if not isinstance(raw, dict):
            return GameEventNotificationOptions.Default(fallback_title=fallback_title, fallback_message=fallback_message)

        delivery = str(raw.get("delivery", "message") or "message").strip()
        severity = str(raw.get("severity", "info") or "info").strip()
        title = raw.get("title", None)
        message = raw.get("message", None)
        color = raw.get("color", None)

        parsed = GameEventNotificationOptions(delivery=delivery, severity=severity, title=title, message=message, color=color)
        if parsed.delivery.lower() in ["none", "off", "hide"]:
            return GameEventNotificationOptions(delivery="none", severity=parsed.severity, title=parsed.title, message=None, color=parsed.color)

        if parsed.message is None:
            parsed.message = str(fallback_message or fallback_title).strip()
        if parsed.title is None:
            parsed.title = str(fallback_title).strip() if str(fallback_title).strip() else None

        return parsed

    def BuildHeaders(self) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "X-Rest-Notify-Delivery": self.delivery,
            "X-Rest-Notify-Severity": self.severity,
        }

        if self.title is not None:
            headers["X-Rest-Notify-Title"] = self.title

        if self.delivery.lower() not in ["none", "off", "hide"] and self.message is not None:
            headers["X-Rest-Notify-Message"] = self.message

        if self.delivery.lower() not in ["none", "off", "hide"] and self.color is not None:
            headers["X-Rest-Notify-Color"] = self.color

        return headers
