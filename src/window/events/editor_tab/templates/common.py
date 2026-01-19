from __future__ import annotations

from typing import Dict


def build_notification(values: Dict[str, object], default_title: str, default_message: str, default_severity: str) -> Dict[str, object]:
    severity = str(values.get("severity", default_severity) or default_severity)
    explicit_delivery = str(values.get("notifyDelivery", "") or "").strip().lower()
    if explicit_delivery in ["none", "message", "letter"]:
        delivery = explicit_delivery
    else:
        use_letter = bool(values.get("useLetter", False))
        delivery = "letter" if use_letter else "message"
    title = str(values.get("notifyTitle", default_title) or default_title)
    message = str(values.get("message", default_message) or default_message)
    color = str(values.get("color", "") or "").strip()

    payload: Dict[str, object] = {
        "delivery": delivery,
        "severity": severity,
        "title": title,
        "message": message,
    }

    if color != "":
        payload["color"] = color

    return payload
