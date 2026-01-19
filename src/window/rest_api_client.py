import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, Optional, Tuple


class RestApiClient:
    """RestApiClient executes configured REST actions."""

    def Execute(self, host: str, port: int, action: Dict[str, object], params: Dict[str, str], headers: Optional[Dict[str, str]] = None) -> str:
        """Execute performs HTTP call.

        Args:
            host: Target host.
            port: API port.
            action: Action config with method/path/payload.
            params: User-provided parameters.

        Returns:
            Short status text.
        """

        safeHost = host or "localhost"
        safePort = port if 0 < port <= 65535 else 8765
        method = str(action.get("method", "GET")).upper()
        pathTemplate = str(action.get("path", "/"))
        payloadKind = str(action.get("payload", "query"))

        renderedPath, remainingParams = self.__RenderPath(pathTemplate, params)

        baseUrl = f"http://{safeHost}:{safePort}".rstrip("/")
        url = f"{baseUrl}{renderedPath}"

        try:
            request, timeoutSeconds = self.__BuildRequest(method, url, payloadKind, remainingParams, headers=headers)
            response = urllib.request.urlopen(request, timeout=timeoutSeconds)
            body = response.read().decode("utf-8", "ignore")
            return self.__Summarize(body)
        except urllib.error.HTTPError as error:
            try:
                body = error.read().decode("utf-8", "ignore")
                summary = self.__Summarize(body)
                return f"HTTP {error.code} {error.reason}: {summary}"
            except Exception:
                return f"HTTP {error.code} {error.reason}"
        except Exception as error:
            return str(error)

    def ExecuteDetailed(self, host: str, port: int, action: Dict[str, object], params: Dict[str, str], headers: Optional[Dict[str, str]] = None) -> Dict[str, object]:
        """ExecuteDetailed performs the HTTP call and returns status + full response body.

        This is intended for debugging/test runs where callers need the full response,
        not just the summarized status text.
        """

        safeHost = host or "localhost"
        safePort = port if 0 < port <= 65535 else 8765
        method = str(action.get("method", "GET")).upper()
        pathTemplate = str(action.get("path", "/"))
        payloadKind = str(action.get("payload", "query"))

        renderedPath, remainingParams = self.__RenderPath(pathTemplate, params)

        baseUrl = f"http://{safeHost}:{safePort}".rstrip("/")
        url = f"{baseUrl}{renderedPath}"

        try:
            request, timeoutSeconds = self.__BuildRequest(method, url, payloadKind, remainingParams, headers=headers)
            response = urllib.request.urlopen(request, timeout=timeoutSeconds)
            body = response.read().decode("utf-8", "ignore")
            status = 0
            try:
                status = int(response.getcode() or 0)
            except Exception:
                status = 0

            return {
                "ok": True,
                "status": status,
                "summary": self.__Summarize(body),
                "body": body,
            }
        except urllib.error.HTTPError as error:
            try:
                body = error.read().decode("utf-8", "ignore")
            except Exception:
                body = ""

            summary = self.__Summarize(body)
            return {
                "ok": False,
                "status": int(getattr(error, "code", 0) or 0),
                "error": f"HTTP {error.code} {error.reason}: {summary}",
                "summary": summary,
                "body": body,
            }
        except Exception as error:
            return {
                "ok": False,
                "status": 0,
                "error": str(error),
                "summary": str(error),
                "body": "",
            }

    def GetJson(self, host: str, port: int, path: str, query: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None) -> object:
        safeHost = host or "localhost"
        safePort = port if 0 < port <= 65535 else 8765
        renderedPath = str(path or "/")

        baseUrl = f"http://{safeHost}:{safePort}".rstrip("/")
        url = f"{baseUrl}{renderedPath}"
        if query:
            url = self.__AttachQuery(url, {str(key): str(value) for key, value in dict(query).items()})

        request = urllib.request.Request(url, method="GET")
        self.__ApplyHeaders(request, headers)
        try:
            response = urllib.request.urlopen(request, timeout=10)
            body = response.read().decode("utf-8", "ignore")
            try:
                return json.loads(body)
            except Exception as error:
                raise ValueError(f"Invalid JSON response: {error}")
        except urllib.error.HTTPError as error:
            try:
                body = error.read().decode("utf-8", "ignore")
            except Exception:
                body = ""

            summary = self.__Summarize(body)
            return {
                "success": False,
                "status": int(getattr(error, "code", 0) or 0),
                "error": f"HTTP {getattr(error, 'code', '')} {getattr(error, 'reason', '')}: {summary}".strip(),
                "body": body,
                "url": url,
            }
        except Exception as error:
            return {
                "success": False,
                "status": 0,
                "error": str(error),
                "body": "",
                "url": url,
            }

    def __BuildRequest(self, method: str, url: str, payloadKind: str, params: Dict[str, str], headers: Optional[Dict[str, str]]) -> Tuple[urllib.request.Request, int]:
        if method == "GET":
            finalUrl = self.__AttachQuery(url, params)
            request = urllib.request.Request(finalUrl, method="GET")
            self.__ApplyHeaders(request, headers)
            return request, 8

        if payloadKind == "json":
            jsonBody: Dict[str, object] = {}
            for key, value in params.items():
                jsonBody[key] = self.__CoerceValue(value)
            dataBytes = json.dumps(jsonBody).encode("utf-8")
            request = urllib.request.Request(url, data=dataBytes, method=method)
            request.add_header("Content-Type", "application/json")
            self.__ApplyHeaders(request, headers)
            return request, 10

        finalUrl = self.__AttachQuery(url, params)
        request = urllib.request.Request(finalUrl, data=b"", method=method)
        self.__ApplyHeaders(request, headers)
        return request, 8

    def __ApplyHeaders(self, request: urllib.request.Request, headers: Optional[Dict[str, str]]) -> None:
        if not headers:
            return
        for headerName, headerValue in headers.items():
            if headerName and headerValue is not None:
                request.add_header(str(headerName), str(headerValue))

    def __RenderPath(self, pathTemplate: str, params: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
        rendered = pathTemplate
        remaining: Dict[str, str] = dict(params or {})
        for key, value in list(remaining.items()):
            placeholder = "{" + str(key) + "}"
            if placeholder in rendered:
                rendered = rendered.replace(placeholder, urllib.parse.quote(str(value)))
                del remaining[key]
        return rendered, remaining

    def __AttachQuery(self, url: str, params: Dict[str, str]) -> str:
        if not params:
            return url
        encoded = urllib.parse.urlencode(params)
        return f"{url}?{encoded}"

    def __CoerceValue(self, value: str) -> object:
        trimmed = (value or "").strip()
        lowered = trimmed.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        try:
            if trimmed != "" and trimmed.isdigit():
                return int(trimmed)
        except Exception:
            pass
        try:
            if trimmed != "" and any(character in trimmed for character in [".", "e", "E"]):
                return float(trimmed)
        except Exception:
            pass
        return value

    def __Summarize(self, body: str) -> str:
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                if "success" in parsed:
                    return f"success: {parsed.get('success')}"
                if "error" in parsed:
                    return str(parsed.get("error"))
                if "errors" in parsed and isinstance(parsed.get("errors"), list) and parsed.get("errors"):
                    return str(parsed.get("errors")[0])
                if "data" in parsed:
                    return "ok"
            if isinstance(parsed, list):
                return f"ok ({len(parsed)})"
        except Exception:
            pass

        trimmed = (body or "").strip()
        if trimmed == "":
            return "Done"
        if len(trimmed) > 160:
            return trimmed[:160] + "..."
        return trimmed
