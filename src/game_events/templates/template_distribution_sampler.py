import random
from typing import Any, Dict, List


class TemplateDistributionSampler:
    def Sample(self, distribution: Dict[str, Any]) -> Any:
        kind = str(distribution.get("kind", "") or "").strip().lower()
        if not kind:
            raise ValueError("Distribution missing required field 'kind'")

        if kind == "fixed":
            return distribution.get("value", None)

        if kind == "choice":
            values = distribution.get("values", [])
            if not isinstance(values, list) or not values:
                raise ValueError("choice distribution requires non-empty 'values' array")
            return random.choice(values)

        if kind == "weighted_choice":
            values = distribution.get("values", [])
            if not isinstance(values, list) or not values:
                raise ValueError("weighted_choice distribution requires non-empty 'values' array")
            choices: List[Any] = []
            weights: List[float] = []
            for item in values:
                if not isinstance(item, dict):
                    continue
                choices.append(item.get("value", None))
                weights.append(float(item.get("weight", 1.0) or 1.0))
            if not choices:
                raise ValueError("weighted_choice distribution has no usable entries")
            return random.choices(choices, weights=weights, k=1)[0]

        if kind == "int_range":
            minimum = int(distribution.get("min", 0) or 0)
            maximum = int(distribution.get("max", 0) or 0)
            if maximum < minimum:
                minimum, maximum = maximum, minimum
            return random.randint(minimum, maximum)

        if kind == "float_range":
            minimum = float(distribution.get("min", 0.0) or 0.0)
            maximum = float(distribution.get("max", 0.0) or 0.0)
            if maximum < minimum:
                minimum, maximum = maximum, minimum
            return random.uniform(minimum, maximum)

        if kind == "bool":
            probabilityTrue = float(distribution.get("probTrue", 0.5) if distribution.get("probTrue", None) is not None else 0.5)
            probabilityTrue = max(0.0, min(probabilityTrue, 1.0))
            return random.random() < probabilityTrue

        raise ValueError(f"Unknown distribution kind: {kind}")
