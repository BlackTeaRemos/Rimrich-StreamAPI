import json
from pathlib import Path
from typing import Any, Dict


class JsoncDocumentLoader:
    def Load(self, filePath: Path) -> Dict[str, Any]:
        text = filePath.read_text(encoding="utf-8")
        cleaned = self.__StripComments(text)
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise ValueError(f"JSONC root must be an object: {filePath}")
        return parsed

    def __StripComments(self, text: str) -> str:
        resultCharacters: list[str] = []
        isInString = False
        isEscaped = False
        index = 0

        while index < len(text):
            character = text[index]
            nextCharacter = text[index + 1] if index + 1 < len(text) else ""

            if isInString:
                resultCharacters.append(character)
                if isEscaped:
                    isEscaped = False
                else:
                    if character == "\\":
                        isEscaped = True
                    elif character == '"':
                        isInString = False
                index += 1
                continue

            # Not in string
            if character == '"':
                isInString = True
                resultCharacters.append(character)
                index += 1
                continue

            # Line comment
            if character == "/" and nextCharacter == "/":
                index += 2
                while index < len(text) and text[index] not in ["\n", "\r"]:
                    index += 1
                continue

            # Block comment
            if character == "/" and nextCharacter == "*":
                index += 2
                while index + 1 < len(text) and not (text[index] == "*" and text[index + 1] == "/"):
                    index += 1
                index += 2 if index + 1 < len(text) else 0
                continue

            resultCharacters.append(character)
            index += 1

        return "".join(resultCharacters)
