# Webhook Display Setup Guide

Display a custom message pushed to FiestaBoard via an HTTP webhook.

## Overview

The Webhook Display plugin exposes a local HTTP endpoint at `/api/plugins/webhook/receive`. Any system can POST a JSON payload and the board will display the configured field. Optionally verify requests with an HMAC-SHA256 secret. No external API required.



### Prerequisites

No API key required. Configure your sender to POST JSON to `/api/plugins/webhook/receive`.

## Quick Setup

1. **Enable** — Go to **Integrations** in your FiestaBoard settings and enable **Webhook Display**.
2. **Configure** — Fill in the plugin settings (see Configuration Reference below).
3. **Template** — Add a page using the `webhook` plugin variables:
   ```
   {{{ webhook.status }}}
   ```
4. **View** — Navigate to your board page to see the live display.

## Template Variables

| Variable | Description | Example |
|---|---|---|
| `webhook.message` | Value of the configured display field from the last payload | `Deploy success!` |
| `webhook.last_updated` | When the last webhook was received | `2026-05-01 12:00` |

## Configuration Reference

| Setting | Name | Description | Default |
|---|---|---|---|
| `enabled` | Enabled |  | `False` |
| `secret` | HMAC Secret | Optional secret to verify incoming webhooks (leave blank to disable). | `` |
| `display_field` | Display Field | JSON field name from the payload to display (e.g. message). | `message` |
| `default_message` | Default Message | Message shown before any webhook is received. | `Waiting for webhook...` |
| `refresh_seconds` | Refresh Interval (seconds) | How often the board polls for new data. | `10` |

## Troubleshooting

- **Message not updating** — verify the POST hits `/api/plugins/webhook/receive` with JSON body.
- **403 Forbidden** — check the HMAC secret matches what your sender is using.

