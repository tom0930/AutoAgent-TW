import json
import logging
from typing import Dict, Any
from .base import BaseRenderer

logger = logging.getLogger("Renderer.Web")

class WebPanelRenderer(BaseRenderer):
    """
    Web Panel Renderer for Antigravity IDE (Phase 171 v2.1).
    Translates Core Events to JSON messages for the IDE Extension.
    """
    def __init__(self, websocket_client=None):
        self.client = websocket_client

    def _send(self, message_type: str, payload: Dict[str, Any]):
        msg = {
            "type": message_type,
            "payload": payload,
            "source": "aa-core-v171"
        }
        # In a real scenario, this sends over WebSocket/MCP to the IDE
        logger.debug(f"WebPanel Send: {json.dumps(msg)}")
        if self.client:
            self.client.send(json.dumps(msg))

    def update_agent_status(self, agent_id: str, status: str, data: Dict[str, Any] = None):
        self._send("agent_status_update", {
            "id": agent_id,
            "status": status,
            "details": data or {}
        })

    def display_suggestion(self, suggestion: Dict[str, Any]):
        self._send("new_suggestion", suggestion)

    def display_squad_metrics(self, squad_id: str, metrics: Dict[str, Any]):
        self._send("squad_metrics", {"id": squad_id, "metrics": metrics})

    def notify_crisis(self, message: str, diagnostic_data: Dict[str, Any]):
        self._send("crisis_alert", {
            "message": message,
            "data": diagnostic_data
        })
