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
    def build_add_hediff(values: Dict[str, object]) -> Dict[str, object]:
        event_id = str(values.get("id", "hediff_add_custom") or "hediff_add_custom").strip()
        label = str(values.get("label", "Add Hediff") or "Add Hediff").strip()
        tags_text = str(values.get("tags", "pawn,hediff") or "pawn,hediff")
        tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()]

        pawn_id = int(values.get("pawnId", 0) or 0)
        hediff_def_name = str(values.get("hediffDefName", "Flu") or "Flu").strip() or "Flu"
        severity_value = float(values.get("hediffSeverity", 0.5) or 0.0)

        notification = build_notification(
            values=values,
            default_title=label,
            default_message=f"Applied hediff: {hediff_def_name}",
            default_severity="neutral",
        )

        return {
            "id": event_id,
            "label": label,
            "cost": int(values.get("cost", 200) or 0),
            "probability": float(values.get("probability", 1.0) or 0.0),
            "tags": tags,
            "notification": notification,
            "requests": [
                {
                    "method": "POST",
                    "path": f"/api/pawns/{pawn_id}/hediffs/add",
                    "payload": "json",
                    "body": {
                        "hediffDefName": hediff_def_name,
                        "severity": severity_value,
                    },
                }
            ],
        }

    return [
        EditorEventTemplate(
            templateId="hediff_add",
            title="Add Hediff",
            description="Adds/updates a hediff on a pawn via POST /api/pawns/{pawnId}/hediffs/add.",
            buildParameters=lambda: [
                StringParameter("id", "Event Id", default="hediff_add_custom"),
                StringParameter("label", "Label", default="Add Hediff"),
                IntSliderParameter("cost", "Cost", minimum=0, maximum=2000, default=200),
                FloatSliderParameter("probability", "Probability", minimum=0.0, maximum=1.0, default=0.9, resolution=0.05),
                StringParameter("tags", "Tags (comma)", default="pawn,hediff"),
                DynamicMappedChoiceParameter("pawnId", "Pawn", fetchOptions=lambda: dataSource.GetPawns(forceRefresh=False), defaultValue=0),
                DynamicChoiceParameter(
                    "hediffDefName",
                    "Hediff Def",
                    fetchOptions=lambda: dataSource.GetHediffCatalog(forceRefresh=False),
                    default="Flu",
                    allowManual=True,
                ),
                FloatSliderParameter("hediffSeverity", "Severity", minimum=0.01, maximum=5.0, default=0.5, resolution=0.05),
                ChoiceParameter("notifyDelivery", "Notify Delivery", options=["none", "message", "letter"], default="letter"),
                ChoiceParameter("severity", "Notification", options=["neutral", "positive", "negative"], default="neutral"),
                StringParameter("notifyTitle", "Notify Title", default="Hediff"),
                StringParameter("message", "Message", default="Hediff applied."),
                StringParameter("color", "Color (optional)", default=""),
            ],
            buildDocument=build_add_hediff,
        )
    ]
