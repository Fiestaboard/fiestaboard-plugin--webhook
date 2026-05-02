"""Display a custom message pushed to FiestaBoard via an HTTP webhook."""

from __future__ import annotations

import logging
from typing import Any, Dict, List
import requests
import datetime
import hashlib
import hmac

# In-memory store for the last received payload
_last_payload: dict = {}
_last_updated: str = ""

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)

USER_AGENT = "FiestaBoard Webhook Display Plugin (https://github.com/Fiestaboard/fiestaboard-plugin--webhook)"


class WebhookPlugin(PluginBase):
    """Webhook Display plugin for FiestaBoard."""

    @property
    def plugin_id(self) -> str:
        return "webhook"

    def fetch_data(self) -> PluginResult:
        try:
            display_field = self.config.get("display_field") or "message"
            default_message = self.config.get("default_message") or "Waiting for webhook..."

            message = str(_last_payload.get(display_field, default_message))[:22]
            last_updated = _last_updated or "Never"

            return PluginResult(
                available=True,
                data={
                    "message": message,
                    "last_updated": last_updated,
                },
            )
        except Exception as e:
            logger.exception("Error reading webhook payload")
            return PluginResult(available=False, error=str(e))

    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        return []

    def cleanup(self) -> None:
        pass
