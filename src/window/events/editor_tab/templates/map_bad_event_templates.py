from __future__ import annotations

from typing import Dict, List

from src.window.events.editor_tab.editor_event_template import EditorEventTemplate
from src.window.events.editor_tab.game_api_data_source import GameApiDataSource
from src.window.events.editor_tab.parameters.bool_parameter import BoolParameter
from src.window.events.editor_tab.parameters.choice_parameter import ChoiceParameter
from src.window.events.editor_tab.parameters.mapped_choice_parameter import MappedChoiceParameter
from src.window.events.editor_tab.parameters.dynamic_mapped_choice_parameter import DynamicMappedChoiceParameter
from src.window.events.editor_tab.parameters.float_slider_parameter import FloatSliderParameter
from src.window.events.editor_tab.parameters.int_slider_parameter import IntSliderParameter
from src.window.events.editor_tab.parameters.string_parameter import StringParameter
from src.window.events.editor_tab.templates.common import build_notification


def build_templates(dataSource: GameApiDataSource) -> List[EditorEventTemplate]:
    def build_meteorite_shower(values: Dict[str, object]) -> Dict[str, object]:
        event_id = str(values.get("id", "meteorite_shower") or "meteorite_shower").strip()
        label = str(values.get("label", "Meteorite Shower") or "Meteorite Shower").strip()
        tags_text = str(values.get("tags", "event,map,bad") or "event,map,bad")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        mode = str(values.get("mode", "Random") or "Random")
        count = int(values.get("count", 3) or 0)
        if count < 1:
            count = 1
        if count > 25:
            count = 25

        base_body: Dict[str, object] = {
            "mapId": int(values.get("mapId", 0) or 0),
            "mode": mode,
        }
        if mode == "Position":
            base_body["x"] = int(values.get("x", 0) or 0)
            base_body["z"] = int(values.get("z", 0) or 0)

        requests = []
        for _ in range(count):
            requests.append(
                {
                    "method": "POST",
                    "path": "/api/meteorites/spawn",
                    "payload": "json",
                    "body": dict(base_body),
                }
            )

        notification = build_notification(
            values=values,
            default_title=label,
            default_message=f"Meteorite shower: {count} impacts.",
            default_severity="negative" if count >= 8 else "neutral",
        )

        return {
            "id": event_id,
            "label": label,
            "cost": int(values.get("cost", 600) or 0),
            "probability": float(values.get("probability", 1.0) or 0.0),
            "tags": tags,
            "notification": notification,
            "requests": requests,
        }

    def build_incident(values: Dict[str, object]) -> Dict[str, object]:
        event_id = str(values.get("id", "map_bad_event") or "map_bad_event").strip()
        label = str(values.get("label", "Map Incident") or "Map Incident").strip()
        tags_text = str(values.get("tags", "event,map,bad") or "event,map,bad")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        incident_def_name = str(values.get("incidentDefName", "Bombardment") or "Bombardment").strip()

        body: Dict[str, object] = {
            "mapId": int(values.get("mapId", 0) or 0),
            "incidentDefName": incident_def_name,
            "forced": bool(values.get("forced", True)),
            "silent": bool(values.get("silent", True)),
        }

        use_position = bool(values.get("usePosition", False))
        if use_position:
            body["x"] = int(values.get("x", 0) or 0)
            body["z"] = int(values.get("z", 0) or 0)

        try:
            points = float(values.get("points", 0.0) or 0.0)
            if points > 0.0:
                body["points"] = points
        except Exception:
            pass

        notification = build_notification(
            values=values,
            default_title=label,
            default_message=f"Map event executed: {incident_def_name}",
            default_severity=str(values.get("severity", "negative") or "negative"),
        )

        return {
            "id": event_id,
            "label": label,
            "cost": int(values.get("cost", 420) or 0),
            "probability": float(values.get("probability", 1.0) or 0.0),
            "tags": tags,
            "notification": notification,
            "requests": [
                {
                    "method": "POST",
                    "path": "/api/incidents/execute",
                    "payload": "json",
                    "body": body,
                }
            ],
        }

    return [
        EditorEventTemplate(
            templateId="meteorite_shower",
            title="Meteorite Shower (Map)",
            description="Runs multiple meteorite impacts (multi-request event) via POST /api/meteorites/spawn.",
            buildParameters=lambda: [
                StringParameter("id", "Event Id", default="meteorite_shower"),
                StringParameter("label", "Label", default="Meteorite Shower"),
                IntSliderParameter("cost", "Cost", minimum=0, maximum=5000, default=600),
                FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.8, resolution=0.05),
                StringParameter("tags", "Tags (comma)", default="event,map,bad"),
                DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
                IntSliderParameter("count", "Impact Count", minimum=1, maximum=25, default=5),
                ChoiceParameter("mode", "Mode", options=["Random", "Cursor", "Position"], default="Random"),
                IntSliderParameter("x", "X (Position)", minimum=0, maximum=400, default=0),
                IntSliderParameter("z", "Z (Position)", minimum=0, maximum=400, default=0),
                ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="message"),
                ChoiceParameter("severity", "Notification", options=["neutral", "positive", "negative"], default="negative"),
                StringParameter("notifyTitle", "Notify Title", default="Meteorite Shower"),
                StringParameter("message", "Message", default="Meteorites are raining down!"),
                StringParameter("color", "Color (optional)", default=""),
            ],
            buildDocument=build_meteorite_shower,
        ),
        EditorEventTemplate(
            templateId="map_bad_event_incident",
            title="Bombardment / Bullet Rain (Map)",
            description="Executes a map-affecting incident via POST /api/incidents/execute. Defaults to Bombardment; swap incidentDefName to match your mod (e.g. BulletRain).",
            buildParameters=lambda: [
                StringParameter("id", "Event Id", default="map_bad_event"),
                StringParameter("label", "Label", default="Map Incident"),
                IntSliderParameter("cost", "Cost", minimum=0, maximum=5000, default=420),
                FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.8, resolution=0.05),
                StringParameter("tags", "Tags (comma)", default="event,map,bad"),
                DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
                MappedChoiceParameter(
                    "incidentDefName",
                    "Incident",
                    options=[
                        ("Bombardment", "Bombardment"),
                        ("Ship Part Crash", "ShipPartCrash"),
                    ],
                    defaultValue="Bombardment",
                ),
                BoolParameter("forced", "Forced", default=True),
                BoolParameter("silent", "Silent (hide game letter)", default=True),
                BoolParameter("usePosition", "Use Position (x/z)", default=False),
                IntSliderParameter("x", "X", minimum=0, maximum=400, default=0),
                IntSliderParameter("z", "Z", minimum=0, maximum=400, default=0),
                FloatSliderParameter("points", "Points (0=auto)", minimum=0.0, maximum=20000.0, default=0.0, resolution=50.0),
                ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="letter"),
                ChoiceParameter("severity", "Notification", options=["neutral", "positive", "negative"], default="negative"),
                StringParameter("notifyTitle", "Notify Title", default="Map Incident"),
                StringParameter("message", "Message", default="Disaster strikes!"),
                StringParameter("color", "Color (optional)", default="#ff5555"),
            ],
            buildDocument=build_incident,
        ),
    ]
