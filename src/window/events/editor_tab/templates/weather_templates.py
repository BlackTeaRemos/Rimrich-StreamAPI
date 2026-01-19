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
    def build_incident(values: Dict[str, object]) -> Dict[str, object]:
        event_id = str(values.get("id", "weather_event") or "weather_event").strip()
        label = str(values.get("label", "Weather") or "Weather").strip()
        tags_text = str(values.get("tags", "event,weather") or "event,weather")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        incident_def_name = str(values.get("incidentDefName", "HeatWave") or "HeatWave").strip()

        body: Dict[str, object] = {
            "mapId": int(values.get("mapId", 0) or 0),
            "incidentDefName": incident_def_name,
            "forced": bool(values.get("forced", True)),
            "silent": bool(values.get("silent", True)),
        }

        try:
            points = float(values.get("points", 0.0) or 0.0)
            if points > 0.0:
                body["points"] = points
        except Exception:
            pass

        notification = build_notification(
            values=values,
            default_title=label,
            default_message=f"Weather event executed: {incident_def_name}",
            default_severity=str(values.get("severity", "neutral") or "neutral"),
        )

        return {
            "id": event_id,
            "label": label,
            "cost": int(values.get("cost", 240) or 0),
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

    def parameters(default_incident: str, default_label: str, default_message: str, default_severity: str) -> List[object]:
        return [
            StringParameter("id", "Event Id", default="weather_event"),
            StringParameter("label", "Label", default=default_label),
            IntSliderParameter("cost", "Cost", minimum=0, maximum=5000, default=240),
            FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.9, resolution=0.05),
            StringParameter("tags", "Tags (comma)", default="event,weather"),
            DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
            MappedChoiceParameter(
                "incidentDefName",
                "Incident",
                options=[
                    ("Heat Wave", "HeatWave"),
                    ("Cold Snap", "ColdSnap"),
                    ("Toxic Fallout", "ToxicFallout"),
                    ("Fog", "Fog"),
                    ("Flashstorm", "Flashstorm"),
                    ("Rain", "Rain"),
                ],
                defaultValue=default_incident,
                helpText="Weather is driven by incidents in vanilla RimWorld; swap incidentDefName if your storyteller/defs differ.",
            ),
            BoolParameter("forced", "Forced", default=True),
            BoolParameter("silent", "Silent (hide game letter)", default=True),
            FloatSliderParameter("points", "Points (0=auto)", minimum=0.0, maximum=20000.0, default=0.0, resolution=50.0),
            ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="message"),
            ChoiceParameter("severity", "Notification", options=["neutral", "positive", "negative"], default=default_severity),
            StringParameter("notifyTitle", "Notify Title", default=default_label),
            StringParameter("message", "Message", default=default_message),
            StringParameter("color", "Color (optional)", default=""),
        ]

    return [
        EditorEventTemplate(
            templateId="weather_heat",
            title="Weather: Heat Wave",
            description="Triggers a heat wave via POST /api/incidents/execute.",
            buildParameters=lambda: parameters(
                default_incident="HeatWave",
                default_label="Heat Wave",
                default_message="A heat wave begins.",
                default_severity="negative",
            ),
            buildDocument=build_incident,
        ),
        EditorEventTemplate(
            templateId="weather_rain",
            title="Weather: Rain",
            description="Triggers a rain-related incident (often Rain) via POST /api/incidents/execute.",
            buildParameters=lambda: parameters(
                default_incident="Rain",
                default_label="Rain",
                default_message="Rain begins to fall.",
                default_severity="neutral",
            ),
            buildDocument=build_incident,
        ),
        EditorEventTemplate(
            templateId="weather_toxic_fallout",
            title="Weather: Toxic Fallout",
            description="Triggers toxic fallout via POST /api/incidents/execute.",
            buildParameters=lambda: parameters(
                default_incident="ToxicFallout",
                default_label="Toxic Fallout",
                default_message="Toxic fallout descends upon the map.",
                default_severity="negative",
            ),
            buildDocument=build_incident,
        ),
    ]
