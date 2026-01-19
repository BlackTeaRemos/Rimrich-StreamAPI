from __future__ import annotations

from typing import Dict, List

from src.window.events.editor_tab.editor_event_template import EditorEventTemplate
from src.window.events.editor_tab.game_api_data_source import GameApiDataSource
from src.window.events.editor_tab.parameters.bool_parameter import BoolParameter
from src.window.events.editor_tab.parameters.choice_parameter import ChoiceParameter
from src.window.events.editor_tab.parameters.dynamic_choice_parameter import DynamicChoiceParameter
from src.window.events.editor_tab.parameters.dynamic_mapped_choice_parameter import DynamicMappedChoiceParameter
from src.window.events.editor_tab.parameters.float_slider_parameter import FloatSliderParameter
from src.window.events.editor_tab.parameters.int_slider_parameter import IntSliderParameter
from src.window.events.editor_tab.parameters.string_parameter import StringParameter
from src.window.events.editor_tab.templates.common import build_notification


def build_templates(dataSource: GameApiDataSource) -> List[EditorEventTemplate]:
    def build_execute_incident(values: Dict[str, object]) -> Dict[str, object]:
        event_id = str(values.get("id", "incident_custom") or "incident_custom").strip()
        label = str(values.get("label", "Execute Incident") or "Execute Incident").strip()
        tags_text = str(values.get("tags", "event,incident") or "event,incident")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        incident_def_name = str(values.get("incidentDefName", "") or "").strip() or "ShortCircuit"
        faction_def_name = str(values.get("factionDefName", "") or "").strip()

        body: Dict[str, object] = {
            "mapId": int(values.get("mapId", 0) or 0),
            "incidentDefName": incident_def_name,
            "forced": bool(values.get("forced", False)),
            "silent": bool(values.get("silent", True)),
        }

        try:
            points = float(values.get("points", 0.0) or 0.0)
            if points > 0.0:
                body["points"] = points
        except Exception:
            pass

        if faction_def_name != "":
            body["factionDefName"] = faction_def_name

        use_position = bool(values.get("usePosition", False))
        if use_position:
            body["x"] = int(values.get("x", 0) or 0)
            body["z"] = int(values.get("z", 0) or 0)

        notification = build_notification(
            values=values,
            default_title=label,
            default_message=f"Incident executed: {incident_def_name}",
            default_severity="neutral",
        )

        return {
            "id": event_id,
            "label": label,
            "cost": int(values.get("cost", 250) or 0),
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
            templateId="incident_execute",
            title="Execute Incident",
            description="Executes an incident via POST /api/incidents/execute. Defaults to silent=true to suppress the game's own letter/message; uses the event's notification instead.",
            buildParameters=lambda: [
                StringParameter("id", "Event Id", default="incident_custom"),
                StringParameter("label", "Label", default="Execute Incident"),
                IntSliderParameter("cost", "Cost", minimum=0, maximum=2000, default=250),
                FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.9, resolution=0.05),
                StringParameter("tags", "Tags (comma)", default="event,incident"),
                DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
                DynamicChoiceParameter(
                    "incidentDefName",
                    "Incident Def",
                    fetchOptions=lambda: dataSource.GetIncidentCatalog(forceRefresh=False),
                    default="ShortCircuit",
                    allowManual=True,
                ),
                BoolParameter("forced", "Forced", default=False),
                BoolParameter("silent", "Silent (hide game letter)", default=True),
                FloatSliderParameter("points", "Points (0=auto)", minimum=0.0, maximum=20000.0, default=0.0, resolution=50.0),
                DynamicChoiceParameter(
                    "factionDefName",
                    "Faction (optional)",
                    fetchOptions=lambda: dataSource.GetFactions(forceRefresh=False),
                    default="",
                    allowManual=True,
                ),
                BoolParameter("usePosition", "Use Position (x/z)", default=False),
                IntSliderParameter("x", "X", minimum=0, maximum=400, default=0),
                IntSliderParameter("z", "Z", minimum=0, maximum=400, default=0),
                ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="letter"),
                ChoiceParameter("severity", "Notification", options=["neutral", "positive", "negative"], default="neutral"),
                StringParameter("notifyTitle", "Notify Title", default="Execute Incident"),
                StringParameter("message", "Message", default="Incident executed."),
                StringParameter("color", "Color (optional)", default=""),
            ],
            buildDocument=build_execute_incident,
        )
    ]
