from __future__ import annotations

from typing import Dict, List

from src.window.events.editor_tab.editor_event_template import EditorEventTemplate
from src.window.events.editor_tab.game_api_data_source import GameApiDataSource
from src.window.events.editor_tab.parameters.bool_parameter import BoolParameter
from src.window.events.editor_tab.parameters.choice_parameter import ChoiceParameter
from src.window.events.editor_tab.parameters.dynamic_mapped_choice_parameter import DynamicMappedChoiceParameter
from src.window.events.editor_tab.parameters.float_slider_parameter import FloatSliderParameter
from src.window.events.editor_tab.parameters.int_slider_parameter import IntSliderParameter
from src.window.events.editor_tab.parameters.string_parameter import StringParameter
from src.window.events.editor_tab.templates.common import build_notification


def build_templates(dataSource: GameApiDataSource) -> List[EditorEventTemplate]:
    def build_meteorite(values: Dict[str, object]) -> Dict[str, object]:
        event_id = str(values.get("id", "meteorite_custom") or "meteorite_custom").strip()
        label = str(values.get("label", "Meteorite") or "Meteorite").strip()
        tags_text = str(values.get("tags", "event,meteorite") or "event,meteorite")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        mode = str(values.get("mode", "Random") or "Random")
        body: Dict[str, object] = {
            "mapId": int(values.get("mapId", 0) or 0),
            "mode": mode,
        }

        if mode == "Position":
            body["x"] = int(values.get("x", 0) or 0)
            body["z"] = int(values.get("z", 0) or 0)

        notification = build_notification(
            values=values,
            default_title=label,
            default_message="A meteorite is falling!",
            default_severity="neutral",
        )

        return {
            "id": event_id,
            "label": label,
            "cost": int(values.get("cost", 220) or 0),
            "probability": float(values.get("probability", 1.0) or 0.0),
            "tags": tags,
            "notification": notification,
            "requests": [
                {
                    "method": "POST",
                    "path": "/api/meteorites/spawn",
                    "payload": "json",
                    "body": body,
                }
            ],
        }

    return [
        EditorEventTemplate(
            templateId="meteorite",
            title="Meteorite",
            description="Spawns a meteorite impact via POST /api/meteorites/spawn.",
            buildParameters=lambda: [
                StringParameter("id", "Event Id", default="meteorite_custom"),
                StringParameter("label", "Label", default="Meteorite"),
                IntSliderParameter("cost", "Cost", minimum=0, maximum=2000, default=220),
                FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.9, resolution=0.05),
                StringParameter("tags", "Tags (comma)", default="event,meteorite"),
                DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
                ChoiceParameter("mode", "Mode", options=["Random", "Cursor", "Position"], default="Random"),
                IntSliderParameter("x", "X (Position)", minimum=0, maximum=400, default=0),
                IntSliderParameter("z", "Z (Position)", minimum=0, maximum=400, default=0),
                ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="message"),
                ChoiceParameter("severity", "Notification", options=["neutral", "positive", "negative"], default="neutral"),
                StringParameter("notifyTitle", "Notify Title", default="Meteorite"),
                StringParameter("message", "Message", default="A meteorite is falling!"),
                StringParameter("color", "Color (optional)", default=""),
            ],
            buildDocument=build_meteorite,
        )
    ]
