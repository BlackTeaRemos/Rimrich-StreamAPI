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
        event_id = str(values.get("id", "global_event") or "global_event").strip()
        label = str(values.get("label", "Global Event") or "Global Event").strip()
        tags_text = str(values.get("tags", "event,global") or "event,global")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        incident_def_name = str(values.get("incidentDefName", "PsychicSoothe") or "PsychicSoothe").strip()

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
            default_message=f"Global event executed: {incident_def_name}",
            default_severity=str(values.get("severity", "neutral") or "neutral"),
        )

        return {
            "id": event_id,
            "label": label,
            "cost": int(values.get("cost", 380) or 0),
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
            StringParameter("id", "Event Id", default="global_event"),
            StringParameter("label", "Label", default=default_label),
            IntSliderParameter("cost", "Cost", minimum=0, maximum=5000, default=380),
            FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.85, resolution=0.05),
            StringParameter("tags", "Tags (comma)", default="event,global"),
            DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
            MappedChoiceParameter(
                "incidentDefName",
                "Incident",
                options=[
                    ("Psychic Soothe", "PsychicSoothe"),
                    ("Earthquake", "Earthquake"),
                    ("Psychic Drone", "PsychicDrone"),
                ],
                defaultValue=default_incident,
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
            templateId="global_psychic_soothe",
            title="Global Event: Psychic Soothe",
            description="Executes a global positive effect (PsychicSoothe) via POST /api/incidents/execute.",
            buildParameters=lambda: parameters(
                default_incident="PsychicSoothe",
                default_label="Psychic Soothe",
                default_message="A calming psychic wave soothes the colony.",
                default_severity="positive",
                default_color="#55ff55",
            ),
            buildDocument=build_incident,
        ),
        EditorEventTemplate(
            templateId="global_tremor",
            title="Global Event: Tremor (Earthquake)",
            description="Executes a global tremor effect (Earthquake) via POST /api/incidents/execute.",
            buildParameters=lambda: parameters(
                default_incident="Earthquake",
                default_label="Earthquake",
                default_message="The ground trembles violently!",
                default_severity="negative",
                default_color="#ff5555",
            ),
            buildDocument=build_incident,
        ),
    ]
