"""Tests for the webhook plugin."""

from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path

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

    def test_fetch_data_returns_default_before_receive(self, configured_plugin):
        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.error is None
        assert result.data is not None
        assert result.data["message"] == "Waiting for webhook..."
        assert result.data["last_updated"] == "Never"

    def test_fetch_data_after_receive(self, configured_plugin):
        configured_plugin.receive_payload({"message": "Deploy success!"}, {})

        result = configured_plugin.fetch_data()

        assert result.available is True
        assert result.data["message"] == "Deploy success!"
        assert result.data["last_updated"] != "Never"

    def test_receive_payload_custom_display_field(self, plugin):
        plugin.config = {"display_field": "status"}
        plugin.receive_payload({"status": "OK", "message": "ignored"}, {})

        result = plugin.fetch_data()

        assert result.data["message"] == "OK"

    def test_receive_payload_preserves_full_message(self, configured_plugin):
        configured_plugin.receive_payload({"message": "A" * 30}, {})

        result = configured_plugin.fetch_data()

        assert result.data["message"] == "A" * 30
        assert len(result.data["message"]) == 30

    def test_receive_payload_hmac_valid(self, plugin):
        secret = "mysecret"
        plugin.config = {"secret": secret, "display_field": "message"}
        raw_body = b'{"message":"hello"}'
        sig = "sha256=" + hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()

        plugin.receive_payload({"message": "hello"}, {"x-webhook-signature": sig}, raw_body=raw_body)

        assert plugin.fetch_data().data["message"] == "hello"

    def test_receive_payload_hmac_invalid_raises(self, plugin):
        plugin.config = {"secret": "correct", "display_field": "message"}
        raw_body = b'{"message":"hello"}'

        with pytest.raises(PermissionError):
            plugin.receive_payload(
                {"message": "hello"},
                {"x-webhook-signature": "sha256=badhash"},
                raw_body=raw_body,
            )

    def test_receive_payload_hmac_missing_raises(self, plugin):
        plugin.config = {"secret": "mysecret", "display_field": "message"}

        with pytest.raises(PermissionError):
            plugin.receive_payload({"message": "hello"}, {})

    def test_receive_payload_no_secret_skips_verification(self, plugin):
        plugin.config = {"secret": "", "display_field": "message"}

        plugin.receive_payload({"message": "hello"}, {})

        assert plugin.fetch_data().data["message"] == "hello"
