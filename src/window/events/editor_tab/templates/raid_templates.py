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
    def build_raid(values: Dict[str, object]) -> Dict[str, object]:
        event_id = str(values.get("id", "raid_custom") or "raid_custom").strip()
        label = str(values.get("label", "Raid") or "Raid").strip()
        tags_text = str(values.get("tags", "event,raid") or "event,raid")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        notification = build_notification(
            values=values,
            default_title=label,
            default_message="A raid was triggered.",
            default_severity="negative",
        )

        preset = str(values.get("raidPreset", "Custom") or "Custom").strip()
        default_faction = str(values.get("factionDefName", "") or "").strip()
        if default_faction == "":
            if preset == "Mechanoids":
                default_faction = "Mechanoid"
            elif preset == "Insects":
                default_faction = "Insect"
            else:
                default_faction = "Pirate"

        points_factor = float(values.get("pointsFactor", 1.0) or 0.0)
        difficulty = str(values.get("difficulty", "Custom") or "Custom").strip()
        if difficulty == "Easy":
            points_factor = 0.6
        elif difficulty == "Normal":
            points_factor = 1.0
        elif difficulty == "Hard":
            points_factor = 1.6
        elif difficulty == "Extreme":
            points_factor = 2.5

        body: Dict[str, object] = {
            "mapId": int(values.get("mapId", 0) or 0),
            "factionDefName": default_faction,
            "method": str(values.get("method", "Incident") or "Incident"),
            "silent": bool(values.get("silent", True)),
            "pointsFactor": points_factor,
        }

        incident_def_name = str(values.get("incidentDefName", "") or "").strip()
        if incident_def_name != "":
            body["incidentDefName"] = incident_def_name

        try:
            points_override = float(values.get("pointsOverride", 0.0) or 0.0)
            if points_override > 0.0:
                body["pointsOverride"] = points_override
        except Exception:
            pass

        for optional_key in ["raidStrategyDefName", "arrivalModeDefName", "pawnKindDefName"]:
            try:
                text = str(values.get(optional_key, "") or "").strip()
                if text != "":
                    body[optional_key] = text
            except Exception:
                continue

        try:
            pawn_count = int(values.get("pawnCount", 0) or 0)
            if pawn_count > 0:
                body["pawnCount"] = pawn_count
        except Exception:
            pass

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
                    "path": "/api/raids/spawn",
                    "payload": "json",
                    "body": body,
                }
            ],
        }

    def build_parameters(default_label: str, default_message: str, default_color: str) -> List[object]:
        return [
            StringParameter("id", "Event Id", default="raid_custom"),
            StringParameter("label", "Label", default=default_label),
            IntSliderParameter("cost", "Cost", minimum=0, maximum=2000, default=420),
            FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.9, resolution=0.05),
            StringParameter("tags", "Tags (comma)", default="event,raid"),
            DynamicMappedChoiceParameter("mapId", "Map", fetchOptions=lambda: dataSource.GetMaps(forceRefresh=False), defaultValue=0),
            ChoiceParameter("raidPreset", "Raid Type", options=["Custom", "Humans", "Mechanoids", "Insects"], default="Humans"),
            DynamicChoiceParameter("factionDefName", "Faction (optional override)", fetchOptions=lambda: dataSource.GetFactions(forceRefresh=False), default="", allowManual=True),
            MappedChoiceParameter(
                "method",
                "Method",
                options=[("Incident", "Incident"), ("Direct Pawns", "DirectPawns")],
                defaultValue="Incident",
            ),
            BoolParameter("silent", "Silent (hide game letter, Incident only)", default=True),
            DynamicChoiceParameter(
                "incidentDefName",
                "Incident (optional override)",
                fetchOptions=lambda: dataSource.GetIncidentCatalog(forceRefresh=False),
                default="",
                allowManual=True,
            ),
            ChoiceParameter("difficulty", "Difficulty", options=["Custom", "Easy", "Normal", "Hard", "Extreme"], default="Normal"),
            FloatSliderParameter("pointsFactor", "Points Factor (Custom)", minimum=0.1, maximum=5.0, default=1.0, resolution=0.1),
            FloatSliderParameter("pointsOverride", "Points Override", minimum=0.0, maximum=20000.0, default=0.0, resolution=50.0),
            DynamicChoiceParameter(
                "raidStrategyDefName",
                "Raid Strategy",
                fetchOptions=lambda: dataSource.GetRaidCatalog(forceRefresh=False).get("raidStrategyDefName", []),
                default="",
                allowManual=True,
            ),
            DynamicChoiceParameter(
                "arrivalModeDefName",
                "Arrival Mode",
                fetchOptions=lambda: dataSource.GetRaidCatalog(forceRefresh=False).get("arrivalModeDefName", []),
                default="",
                allowManual=True,
            ),
            DynamicChoiceParameter(
                "pawnKindDefName",
                "Pawn Kind (Direct)",
                fetchOptions=lambda: dataSource.GetPawnKinds(presentOnly=False, forceRefresh=False),
                default="",
                allowManual=True,
            ),
            IntSliderParameter("pawnCount", "Pawn Count (Direct)", minimum=1, maximum=200, default=10),
            ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="letter"),
            ChoiceParameter("severity", "Notification", options=["negative", "neutral", "positive"], default="negative"),
            StringParameter("notifyTitle", "Notify Title", default=default_label),
            StringParameter("message", "Message", default=default_message),
            StringParameter("color", "Color (optional)", default=default_color),
        ]

    return [
        EditorEventTemplate(
            templateId="raid_humans",
            title="Raid (Humans)",
            description="Triggers an enemy raid via POST /api/raids/spawn. Uses Incident method by default, with silent=true to suppress the game's own letter/message.",
            buildParameters=lambda: build_parameters(
                default_label="Raid (Humans)",
                default_message="A human raid was triggered by Twitch.",
                default_color="#ff5555",
            ),
            buildDocument=build_raid,
        ),
        EditorEventTemplate(
            templateId="raid_mechanoids",
            title="Raid (Mechanoids)",
            description="Triggers a mechanoid raid (faction defaults to Mechanoid) via POST /api/raids/spawn.",
            buildParameters=lambda: build_parameters(
                default_label="Raid (Mechanoids)",
                default_message="A mechanoid raid was triggered by Twitch.",
                default_color="#ff7777",
            ),
            buildDocument=lambda values: build_raid({**values, "raidPreset": "Mechanoids"}),
        ),
        EditorEventTemplate(
            templateId="raid_insects",
            title="Raid (Insects)",
            description="Triggers an insect raid (faction defaults to Insect) via POST /api/raids/spawn.",
            buildParameters=lambda: build_parameters(
                default_label="Raid (Insects)",
                default_message="An insect raid was triggered by Twitch.",
                default_color="#ff7777",
            ),
            buildDocument=lambda values: build_raid({**values, "raidPreset": "Insects"}),
        ),
    ]
