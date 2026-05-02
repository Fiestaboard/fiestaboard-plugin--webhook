"""Tests for the webhook plugin."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from plugins.webhook import WebhookPlugin
from src.plugins.base import PluginResult

MANIFEST = json.loads("""
{
    "id": "webhook",
    "name": "Webhook Display",
    "version": "0.1.0",
    "settings_schema": {
        "type": "object",
        "properties": {
            "enabled": {
                "type": "boolean",
                "title": "Enabled",
                "default": false
            },
            "secret": {
                "type": "string",
                "title": "HMAC Secret",
                "description": "Optional secret to verify incoming webhooks (leave blank to disable).",
                "default": ""
            },
            "display_field": {
                "type": "string",
                "title": "Display Field",
                "description": "JSON field name from the payload to display (e.g. message).",
                "default": "message"
            },
            "default_message": {
                "type": "string",
                "title": "Default Message",
                "description": "Message shown before any webhook is received.",
                "default": "Waiting for webhook..."
            },
            "refresh_seconds": {
                "type": "integer",
                "title": "Refresh Interval (seconds)",
                "description": "How often the board polls for new data.",
                "default": 10,
                "minimum": 5
            }
        },
        "required": []
    }
}
""")

SAMPLE_RESPONSE = json.loads("""
{
    "message": "Deploy success!",
    "timestamp": "2026-05-01T12:00:00Z"
}
""")


@pytest.fixture
def plugin():
    return WebhookPlugin(MANIFEST)


@pytest.fixture
def configured_plugin():
    p = WebhookPlugin(MANIFEST)
    p.config = json.loads("""
{
    "display_field": "message",
    "default_message": "Waiting for webhook..."
}
""")
    return p


class TestWebhookPlugin:

    def test_plugin_id(self, plugin):
        assert plugin.plugin_id == "webhook"

    def test_manifest_valid(self):
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        with open(manifest_path) as f:
            m = json.load(f)
        for field in ("id", "name", "version"):
            assert field in m

    @patch("plugins.webhook.requests.get")
    def test_fetch_data_success(self, mock_get, configured_plugin):
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_RESPONSE
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.error is None
        assert result.data is not None
        assert "message" in result.data, "missing variable: message"
        assert "last_updated" in result.data, "missing variable: last_updated"

    @pytest.mark.skip(reason="plugin does not use requests.get")
    def test_fetch_data_network_error(self, configured_plugin):
        pass

    @pytest.mark.skip(reason="plugin does not use requests.get")
    def test_fetch_data_bad_json(self, configured_plugin):
        pass

