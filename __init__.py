"""Display a custom message pushed to FiestaBoard via an HTTP webhook."""

from __future__ import annotations

import datetime
import hashlib
import hmac
import json
import logging
from typing import Any, Dict, List

from src.plugins.base import PluginBase, PluginResult

logger = logging.getLogger(__name__)


class WebhookPlugin(PluginBase):
    """Webhook Display plugin for FiestaBoard."""

    def __init__(self, manifest: Dict[str, Any]) -> None:
        super().__init__(manifest)
        self._payload: Dict[str, Any] = {}
        self._last_updated: str = ""

    @property
    def plugin_id(self) -> str:
        return "webhook"

    def receive_payload(
        self,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        raw_body: bytes = b"",
    ) -> None:
        secret = self.config.get("secret", "")
        if secret:
            sig_header = headers.get("x-webhook-signature", "")
            if not sig_header:
                raise PermissionError("Missing X-Webhook-Signature header")
            body_bytes = raw_body if raw_body else json.dumps(payload, separators=(",", ":")).encode()
            expected = "sha256=" + hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig_header, expected):
                raise PermissionError("Invalid webhook signature")
        self._payload = payload
        self._last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def fetch_data(self) -> PluginResult:
        try:
            display_field = self.config.get("display_field") or "message"
            default_message = self.config.get("default_message") or "Waiting for webhook..."

            message = str(self._payload.get(display_field, default_message))
            last_updated = self._last_updated or "Never"

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
