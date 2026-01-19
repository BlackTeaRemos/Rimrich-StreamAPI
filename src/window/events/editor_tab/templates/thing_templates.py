from __future__ import annotations

from typing import Dict, List

from src.window.events.editor_tab.editor_event_template import EditorEventTemplate
from src.window.events.editor_tab.game_api_data_source import GameApiDataSource
from src.window.events.editor_tab.parameters.bool_parameter import BoolParameter
from src.window.events.editor_tab.parameters.choice_parameter import ChoiceParameter
from src.window.events.editor_tab.parameters.mapped_choice_parameter import MappedChoiceParameter
from src.window.events.editor_tab.parameters.dynamic_choice_parameter import DynamicChoiceParameter
from src.window.events.editor_tab.parameters.dynamic_mapped_choice_parameter import DynamicMappedChoiceParameter
from src.window.events.editor_tab.parameters.float_slider_parameter import FloatSliderParameter
from src.window.events.editor_tab.parameters.int_slider_parameter import IntSliderParameter
from src.window.events.editor_tab.parameters.string_parameter import StringParameter
from src.window.events.editor_tab.templates.common import build_notification


def build_templates(dataSource: GameApiDataSource) -> List[EditorEventTemplate]:
    def build_spawn_thing(values: Dict[str, object]) -> Dict[str, object]:
        event_id = str(values.get("id", "spawn_thing_custom") or "spawn_thing_custom").strip()
        label = str(values.get("label", "Spawn Thing") or "Spawn Thing").strip()
        tags_text = str(values.get("tags", "spawn,thing") or "spawn,thing")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        mode = str(values.get("mode", "DropPods") or "DropPods")
        body: Dict[str, object] = {
            "mapId": int(values.get("mapId", 0) or 0),
            "thingDefName": str(values.get("thingDefName", "Steel") or "Steel"),
            "count": int(values.get("count", 100) or 0),
            "mode": mode,
        }

        if mode == "Position":
            body["x"] = int(values.get("x", 0) or 0)
            body["z"] = int(values.get("z", 0) or 0)

        notification = build_notification(
            values=values,
            default_title=label,
            default_message="Items spawned.",
            default_severity="positive",
        )

        return {
            "id": event_id,
            "label": label,
            "cost": int(values.get("cost", 120) or 0),
            "probability": float(values.get("probability", 1.0) or 0.0),
            "tags": tags,
            "notification": notification,
            "requests": [
                {
                    "method": "POST",
                    "path": "/api/things/spawn",
                    "payload": "json",
                    "body": body,
                }
            ],
        }

    return [
        EditorEventTemplate(
            templateId="spawn_thing",
            title="Spawn Thing",
            description="Spawns an item via POST /api/things/spawn (DropPods/NearColonists/Edge/Cursor/Position).",
            buildParameters=lambda: [
                StringParameter("id", "Event Id", default="spawn_thing_custom"),
                StringParameter("label", "Label", default="Spawn Thing"),
                IntSliderParameter("cost", "Cost", minimum=0, maximum=2000, default=120),
                FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.9, resolution=0.05),
                StringParameter("tags", "Tags (comma)", default="spawn,thing"),
                DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
                DynamicChoiceParameter(
                    "thingDefName",
                    "Thing Def",
                    fetchOptions=lambda: dataSource.GetThingCatalog(forceRefresh=False),
                    default="Steel",
                    allowManual=True,
                ),
                IntSliderParameter("count", "Count", minimum=1, maximum=5000, default=100),
                MappedChoiceParameter(
                    "mode",
                    "Spawn Mode",
                    options=[
                        ("Drop Pods", "DropPods"),
                        ("Near Colonists", "NearColonists"),
                        ("Edge", "Edge"),
                        ("Cursor", "Cursor"),
                        ("Position", "Position"),
                    ],
                    defaultValue="DropPods",
                ),
                IntSliderParameter("x", "X (Position)", minimum=0, maximum=400, default=0),
                IntSliderParameter("z", "Z (Position)", minimum=0, maximum=400, default=0),
                    ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="message"),
                ChoiceParameter("severity", "Notification", options=["positive", "neutral", "negative"], default="positive"),
                StringParameter("notifyTitle", "Notify Title", default="Spawn Thing"),
                StringParameter("message", "Message", default="Items spawned."),
                StringParameter("color", "Color (optional)", default=""),
            ],
            buildDocument=build_spawn_thing,
        )
    ]
