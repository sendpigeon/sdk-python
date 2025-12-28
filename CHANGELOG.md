# Changelog

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
