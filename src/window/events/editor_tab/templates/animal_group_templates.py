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
        event_id = str(values.get("id", "animals_custom") or "animals_custom").strip()
        label = str(values.get("label", "Animals") or "Animals").strip()
        tags_text = str(values.get("tags", "event,animals") or "event,animals")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        incident_def_name = str(values.get("incidentDefName", "HerdMigration") or "HerdMigration").strip()

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
            default_message=f"Animal event executed: {incident_def_name}",
            default_severity=str(values.get("severity", "neutral") or "neutral"),
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
                    "path": "/api/incidents/execute",
                    "payload": "json",
                    "body": body,
                }
            ],
        }

    def parameters(default_incident: str, default_label: str, default_message: str, default_severity: str) -> List[object]:
        return [
            StringParameter("id", "Event Id", default="animals_custom"),
            StringParameter("label", "Label", default=default_label),
            IntSliderParameter("cost", "Cost", minimum=0, maximum=2000, default=220),
            FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.9, resolution=0.05),
            StringParameter("tags", "Tags (comma)", default="event,animals"),
            DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
            MappedChoiceParameter(
                "incidentDefName",
                "Incident",
                options=[
                    ("Herd Migration", "HerdMigration"),
                    ("Manhunter Pack", "ManhunterPack"),
                    ("Farm Animals Wander In", "FarmAnimalsWanderIn"),
                    ("Self Tame", "SelfTame"),
                ],
                defaultValue=default_incident,
                helpText="These are common vanilla incident defNames. If your game uses different defs, use the generic Execute Incident template.",
            ),
            BoolParameter("forced", "Forced", default=True),
            BoolParameter("silent", "Silent (hide game letter)", default=True),
            FloatSliderParameter("points", "Points (0=auto)", minimum=0.0, maximum=20000.0, default=0.0, resolution=50.0),
            ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="letter"),
            ChoiceParameter("severity", "Notification", options=["neutral", "positive", "negative"], default=default_severity),
            StringParameter("notifyTitle", "Notify Title", default=default_label),
            StringParameter("message", "Message", default=default_message),
            StringParameter("color", "Color (optional)", default=""),
        ]

    return [
        EditorEventTemplate(
            templateId="animals_neutral",
            title="Animals (Neutral Herd)",
            description="Executes a neutral animal group incident (e.g. HerdMigration).",
            buildParameters=lambda: parameters(
                default_incident="HerdMigration",
                default_label="Animals (Neutral)",
                default_message="A herd has arrived.",
                default_severity="neutral",
            ),
            buildDocument=build_incident,
        ),
        EditorEventTemplate(
            templateId="animals_manhunting",
            title="Animals (Manhunter Pack)",
            description="Executes a manhunting animals incident (e.g. ManhunterPack).",
            buildParameters=lambda: parameters(
                default_incident="ManhunterPack",
                default_label="Manhunter Pack",
                default_message="A manhunter pack was triggered by Twitch.",
                default_severity="negative",
            ),
            buildDocument=build_incident,
        ),
        EditorEventTemplate(
            templateId="animals_tamed",
            title="Animals (Tamed / Wander In)",
            description="Executes a tame-animals incident (e.g. FarmAnimalsWanderIn or SelfTame).",
            buildParameters=lambda: parameters(
                default_incident="FarmAnimalsWanderIn",
                default_label="Tame Animals",
                default_message="Tame animals have joined the colony.",
                default_severity="positive",
            ),
            buildDocument=build_incident,
        ),
    ]
