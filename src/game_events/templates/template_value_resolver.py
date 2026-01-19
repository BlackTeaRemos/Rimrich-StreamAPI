from typing import Any, Dict


class TemplateValueResolver:
    def Resolve(self, template: Any, values: Dict[str, Any]) -> Any:
        if isinstance(template, dict):
            if set(template.keys()) == {"$param"}:
                paramName = str(template.get("$param", "") or "")
                return self.__ResolveParam(paramName, values)
            return {str(key): self.Resolve(value, values) for key, value in template.items()}

        if isinstance(template, list):
            return [self.Resolve(value, values) for value in template]

        return template

    def __ResolveParam(self, paramName: str, values: Dict[str, Any]) -> Any:
        name = str(paramName or "").strip()
        if not name:
            raise ValueError("Empty parameter name")

        if "." not in name:
            if name not in values:
                raise ValueError(f"Unknown parameter: {name}")
            return values[name]

        parts = [part.strip() for part in name.split(".") if part.strip()]
        if not parts:
            raise ValueError("Invalid parameter path")

        rootName = parts[0]
        if rootName not in values:
            raise ValueError(f"Unknown parameter: {rootName}")

        current: Any = values[rootName]
        for part in parts[1:]:
            if not isinstance(current, dict):
                raise ValueError(f"Parameter path '{name}' expects an object at '{part}'")
            if part not in current:
                raise ValueError(f"Parameter path '{name}' missing key '{part}'")
            current = current[part]
        return current
