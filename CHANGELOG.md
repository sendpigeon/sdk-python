# Changelog

## 0.6.0

- Add Contacts API (`contacts.list`, `create`, `batch`, `get`, `update`, `delete`, `unsubscribe`, `resubscribe`, `stats`, `tags`)
- Add Broadcasts API (`broadcasts.list`, `create`, `get`, `update`, `delete`, `send`, `schedule`, `cancel`, `test`, `recipients`, `analytics`)
- Broadcast targeting: `include_tags` and `exclude_tags` options
- Both sync and async clients supported

## 0.4.0

- Per-email tracking: `tracking=TrackingOptions(opens=True, clicks=True)` in send requests
- Export `TrackingOptions` type
- Response `warnings` field for non-fatal issues (e.g., tracking disabled at org level)
- Updated `TrackingDefaults` to use `tracking_enabled` master toggle

## 0.3.2

- Fixed version mismatch between pyproject.toml and __init__.py

## 0.3.1

- Added `BatchEmailInput` type for typed batch email sending
- Reduced code duplication between sync/async clients (extracted to `_shared.py`)
- Internal refactoring, no breaking changes

## 0.3.0

- Add Suppressions API (`suppressions.list`, `suppressions.delete`)

## 0.2.0

- Add `email.opened` and `email.clicked` webhook events
- Add typed `WebhookEvent` and `WebhookPayloadData` dataclasses
- Add `WEBHOOK_EVENTS` constant

## 0.1.0

- Initial release
- Send emails (single + batch)
- Templates API
- Domains API
- API Keys API
- Webhook signature verification
- Async client support
