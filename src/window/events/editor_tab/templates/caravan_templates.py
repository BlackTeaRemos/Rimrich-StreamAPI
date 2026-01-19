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
    def build_spawn_caravan(values: Dict[str, object]) -> Dict[str, object]:
        event_id = str(values.get("id", "spawn_caravan_custom") or "spawn_caravan_custom").strip()
        label = str(values.get("label", "Spawn Caravan") or "Spawn Caravan").strip()
        tags_text = str(values.get("tags", "spawn,caravan") or "spawn,caravan")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        notification = build_notification(
            values=values,
            default_title="Twitch",
            default_message=label,
            default_severity="positive",
        )

        return {
            "id": event_id,
            "label": label,
            "cost": int(values.get("cost", 180) or 0),
            "probability": float(values.get("probability", 1.0) or 0.0),
            "tags": tags,
            "notification": notification,
            "requests": [
                {
                    "method": "POST",
                    "path": "/api/caravans/spawn",
                    "payload": "json",
                    "body": {
                        "mapId": int(values.get("mapId", 0) or 0),
                        "factionDefName": str(values.get("factionDefName", "OutlanderCivil") or "OutlanderCivil"),
                        "silent": bool(values.get("silent", True)),
                        "mode": str(values.get("mode", "Auto") or "Auto"),
                    },
                }
            ],
        }

    def build_parameters(default_label: str, default_faction: str, default_severity: str, default_message: str) -> List[object]:
        return [
            StringParameter("id", "Event Id", default="spawn_caravan_custom"),
            StringParameter("label", "Label", default=default_label),
            IntSliderParameter("cost", "Cost", minimum=0, maximum=1000, default=180),
            FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.8, resolution=0.05),
            StringParameter("tags", "Tags (comma)", default="spawn,caravan"),
            DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
            DynamicChoiceParameter("factionDefName", "Faction", fetchOptions=lambda: dataSource.GetFactions(forceRefresh=False), default=default_faction),
            BoolParameter("silent", "Silent (hide game letter)", default=True),
            MappedChoiceParameter(
                "mode",
                "Caravan Mode",
                options=[
                    ("Auto", "Auto"),
                    ("Trader Caravan Arrival", "TraderCaravanArrival"),
                    ("Visitor Group", "VisitorGroup"),
                ],
                defaultValue="Auto",
            ),
            ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="letter"),
            ChoiceParameter("severity", "Notification", options=["positive", "neutral", "negative"], default=default_severity),
            StringParameter("notifyTitle", "Notify Title", default="Twitch"),
            StringParameter("message", "Message", default=default_message),
            StringParameter("color", "Color (optional)", default=""),
        ]

    return [
        EditorEventTemplate(
            templateId="caravan_friendly",
            title="Caravan (Friendly Traders)",
            description="Spawns a friendly trader caravan via POST /api/caravans/spawn. Pawn composition and behavior are chosen by the game.",
            buildParameters=lambda: build_parameters(
                default_label="Caravan (Friendly)",
                default_faction="OutlanderCivil",
                default_severity="positive",
                default_message="A friendly caravan arrives.",
            ),
            buildDocument=build_spawn_caravan,
        ),
        EditorEventTemplate(
            templateId="caravan_hostile",
            title="Caravan (Hostile Passers)",
            description="Spawns a passing group for a hostile faction. If the faction has trader kinds, it may behave like traders; otherwise it will use VisitorGroup behavior.",
            buildParameters=lambda: build_parameters(
                default_label="Caravan (Hostile)",
                default_faction="Pirate",
                default_severity="negative",
                default_message="A hostile group approaches!",
            ),
            buildDocument=lambda values: build_spawn_caravan({**values, "mode": "VisitorGroup"}),
        ),
        EditorEventTemplate(
            templateId="spawn_caravan",
            title="Spawn Caravan (Custom)",
            description="Spawns a caravan via POST /api/caravans/spawn. The game selects caravan composition (pawn kinds/count) automatically.",
            buildParameters=lambda: build_parameters(
                default_label="Spawn Caravan",
                default_faction="OutlanderCivil",
                default_severity="positive",
                default_message="A caravan arrives.",
            ),
            buildDocument=build_spawn_caravan,
        ),
    ]
