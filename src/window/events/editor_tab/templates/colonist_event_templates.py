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
        event_id = str(values.get("id", "colonist_event") or "colonist_event").strip()
        label = str(values.get("label", "Colonist Event") or "Colonist Event").strip()
        tags_text = str(values.get("tags", "event,colonists") or "event,colonists")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        incident_def_name = str(values.get("incidentDefName", "WandererJoin") or "WandererJoin").strip()

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
            default_message=f"Colonist event executed: {incident_def_name}",
            default_severity=str(values.get("severity", "positive") or "positive"),
        )

        return {
            "id": event_id,
            "label": label,
            "cost": int(values.get("cost", 500) or 0),
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

    def parameters(default_incident: str, default_label: str, default_message: str, default_severity: str, default_color: str) -> List[object]:
        return [
            StringParameter("id", "Event Id", default="colonist_event"),
            StringParameter("label", "Label", default=default_label),
            IntSliderParameter("cost", "Cost", minimum=0, maximum=5000, default=500),
            FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.8, resolution=0.05),
            StringParameter("tags", "Tags (comma)", default="event,colonists"),
            DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
            MappedChoiceParameter(
                "incidentDefName",
                "Incident",
                options=[
                    ("Wanderer Joins", "WandererJoin"),
                    ("Transport Pod Crash", "TransportPodCrash"),
                    ("Refugee Chased", "RefugeeChased"),
                ],
                defaultValue=default_incident,
                helpText="These are common vanilla pawn-joining incidents. If you want full control, use the generic Execute Incident template.",
            ),
            BoolParameter("forced", "Forced", default=True),
            BoolParameter("silent", "Silent (hide game letter)", default=True),
            FloatSliderParameter("points", "Points (0=auto)", minimum=0.0, maximum=20000.0, default=0.0, resolution=50.0),
            ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="letter"),
            ChoiceParameter("severity", "Notification", options=["neutral", "positive", "negative"], default=default_severity),
            StringParameter("notifyTitle", "Notify Title", default=default_label),
            StringParameter("message", "Message", default=default_message),
            StringParameter("color", "Color (optional)", default=default_color),
        ]

    return [
        EditorEventTemplate(
            templateId="colonist_join",
            title="Affecting Event: New Colonist (Wanderer)",
            description="Triggers a pawn-joining incident (WandererJoin) via POST /api/incidents/execute.",
            buildParameters=lambda: parameters(
                default_incident="WandererJoin",
                default_label="New Colonist",
                default_message="A new colonist has joined!",
                default_severity="positive",
                default_color="#55ff55",
            ),
            buildDocument=build_incident,
        ),
        EditorEventTemplate(
            templateId="colonist_refugee",
            title="Affecting Event: Refugee Chased",
            description="Triggers a chased refugee event (RefugeeChased) via POST /api/incidents/execute.",
            buildParameters=lambda: parameters(
                default_incident="RefugeeChased",
                default_label="Refugee Chased",
                default_message="A refugee is being chased!",
                default_severity="neutral",
                default_color="",
            ),
            buildDocument=build_incident,
        ),
    ]
