import http.server
import json
import socketserver
import threading
from typing import List, Optional

from src.game_events.game_event_catalog_service import GameEventCatalogService
from src.purchases.interfaces.events_web_server_interface import EventsWebServerInterface


class EventsWebServer(EventsWebServerInterface):
    """Simple HTTP server that displays available events and their costs."""

    def __init__(self, catalogService: GameEventCatalogService) -> None:
        self._catalogService = catalogService
        self._server: Optional[socketserver.TCPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._port = 0

    def Start(self, port: int) -> None:
        """Start the web server on the specified port.

        Args:
            port: The port number to listen on.
        """
        self.Stop()
        self._port = port

        try:
            handlerFactory = self._CreateHandlerFactory()
            self._server = socketserver.TCPServer(("", port), handlerFactory)
            self._server.allow_reuse_address = True
            self._thread = threading.Thread(target=self._RunServer, daemon=True)
            self._thread.start()
            print(f"EventsWebServer: Started on port {port}")
        except Exception as error:
            print(f"EventsWebServer: Failed to start on port {port}: {error}")
            self._server = None
            self._thread = None

    def Stop(self) -> None:
        """Stop the web server."""
        server = self._server
        if server is not None:
            try:
                server.shutdown()
            except Exception:
                pass
            self._server = None
            self._thread = None
            print("EventsWebServer: Stopped")

    def IsRunning(self) -> bool:
        """Check if the web server is currently running.

        Returns:
            bool: True if running, False otherwise.
        """
        return self._server is not None

    def _RunServer(self) -> None:
        """Run the server in a background thread."""
        server = self._server
        if server is not None:
            try:
                server.serve_forever()
            except Exception as error:
                print(f"EventsWebServer: Server error: {error}")

    def _CreateHandlerFactory(self) -> type:
        """Create a request handler class with access to the catalog service."""
        catalogService = self._catalogService

        class EventsRequestHandler(http.server.BaseHTTPRequestHandler):
            """HTTP request handler for events listing."""

            def do_GET(self) -> None:
                """Handle GET requests - serve the events list page."""
                if self.path == "/" or self.path == "/events":
                    self._ServeEventsPage()
                else:
                    self.send_error(404, "Not Found")

            def _ServeEventsPage(self) -> None:
                """Serve the HTML page listing all purchasable events."""
                try:
                    eventsData = self._GetEventsData()
                    htmlContent = self._BuildHtmlPage(eventsData)
                    
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(htmlContent)))
                    self.end_headers()
                    self.wfile.write(htmlContent)
                except Exception as error:
                    self.send_error(500, f"Internal Server Error: {error}")

            def _GetEventsData(self) -> List[dict]:
                """Get all purchasable events as a list of dictionaries."""
                allEvents = catalogService.GetAll()
                eventsData = []
                for eventDefinition in allEvents:
                    if eventDefinition.hidden:
                        continue
                    if eventDefinition.cost <= 0:
                        continue
                    eventsData.append({
                        "id": eventDefinition.eventId,
                        "label": eventDefinition.label,
                        "cost": eventDefinition.cost,
                        "tags": eventDefinition.tags,
                        "userMessage": eventDefinition.userMessage or "",
                    })
                eventsData.sort(key=lambda event: (event["cost"], event["label"]))
                return eventsData

            def _BuildHtmlPage(self, eventsData: List[dict]) -> bytes:
                """Build the HTML page content."""
                eventsHtml = ""
                for event in eventsData:
                    tagsHtml = " ".join(f'<span class="tag">{tag}</span>' for tag in event["tags"])
                    description = event["userMessage"] if event["userMessage"] else ""
                    eventsHtml += f"""
                    <div class="event-card">
                        <div class="event-header">
                            <span class="event-label">{event["label"]}</span>
                            <span class="event-cost">{event["cost"]} silver</span>
                        </div>
                        <div class="event-id">!buy {event["id"]}</div>
                        {f'<div class="event-description">{description}</div>' if description else ''}
                        <div class="event-tags">{tagsHtml}</div>
                    </div>
                    """

                htmlTemplate = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream Events Shop</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #ffd700;
            margin-bottom: 10px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        .subtitle {{
            text-align: center;
            color: #aaa;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .commands {{
            background: rgba(255,255,255,0.1);
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .commands code {{
            background: rgba(0,0,0,0.3);
            padding: 3px 8px;
            border-radius: 4px;
            color: #ffd700;
        }}
        .events-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        .event-card {{
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .event-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border-color: #ffd700;
        }}
        .event-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .event-label {{
            font-size: 1.3em;
            font-weight: bold;
            color: #fff;
        }}
        .event-cost {{
            background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%);
            color: #1a1a2e;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .event-id {{
            font-family: monospace;
            color: #888;
            font-size: 0.9em;
            margin-bottom: 8px;
        }}
        .event-description {{
            color: #bbb;
            font-size: 0.95em;
            margin-bottom: 10px;
            line-height: 1.4;
        }}
        .event-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }}
        .tag {{
            background: rgba(100,100,255,0.2);
            color: #8888ff;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8em;
        }}
        .no-events {{
            text-align: center;
            padding: 50px;
            color: #888;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Stream Events Shop</h1>
        <p class="subtitle">Spend your silver to trigger events in the game!</p>
        
        <div class="commands">
            <p>
                <code>!silver</code> - Check your balance |
                <code>!buy &lt;event&gt;</code> - Purchase an event
            </p>
        </div>
        
        <div class="events-grid">
            {eventsHtml if eventsHtml else '<div class="no-events">No purchasable events available.</div>'}
        </div>
    </div>
</body>
</html>"""
                return htmlTemplate.encode("utf-8")

            def log_message(self, format: str, *args) -> None:
                """Suppress default logging."""
                pass

        return EventsRequestHandler
