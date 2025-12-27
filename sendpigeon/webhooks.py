from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any, Literal, Union


# Webhook event types
WEBHOOK_EVENTS = [
    "email.delivered",
    "email.bounced",
    "email.complained",
    "email.opened",
    "email.clicked",
    "webhook.test",
]


@dataclass
class WebhookPayloadData:
    """Typed webhook payload data."""

    email_id: str | None = None
    to_address: str | None = None
    from_address: str | None = None
    subject: str | None = None
    bounce_type: str | None = None
    complaint_type: str | None = None
    # Present for email.opened events
    opened_at: str | None = None
    # Present for email.clicked events
    clicked_at: str | None = None
    link_url: str | None = None
    link_index: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WebhookPayloadData":
        return cls(
            email_id=data.get("emailId"),
            to_address=data.get("toAddress"),
            from_address=data.get("fromAddress"),
            subject=data.get("subject"),
            bounce_type=data.get("bounceType"),
            complaint_type=data.get("complaintType"),
            opened_at=data.get("openedAt"),
            clicked_at=data.get("clickedAt"),
            link_url=data.get("linkUrl"),
            link_index=data.get("linkIndex"),
        )


@dataclass
class WebhookEvent:
    """Typed webhook event."""

    event: str
    timestamp: str
    data: WebhookPayloadData

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "WebhookEvent":
        return cls(
            event=payload.get("event", ""),
            timestamp=payload.get("timestamp", ""),
            data=WebhookPayloadData.from_dict(payload.get("data", {})),
        )


@dataclass
class WebhookVerifySuccess:
    """Successful webhook verification result."""

    valid: Literal[True]
    payload: dict[str, Any]


@dataclass
class WebhookVerifyFailure:
    """Failed webhook verification result."""

    valid: Literal[False]
    error: str


WebhookVerifyResult = Union[WebhookVerifySuccess, WebhookVerifyFailure]


def verify_webhook(
    *,
    payload: str | bytes,
    signature: str,
    timestamp: str,
    secret: str,
    max_age: int = 300,
) -> WebhookVerifyResult:
    """
    Verify a webhook signature from SendPigeon.

    Args:
        payload: Raw request body (string or bytes)
        signature: Value of X-Webhook-Signature header
        timestamp: Value of X-Webhook-Timestamp header
        secret: Your webhook secret from dashboard
        max_age: Maximum age of webhook in seconds (default: 300 = 5 minutes)

    Returns:
        WebhookVerifyResult with valid=True and payload, or valid=False and error

    Example:
        >>> result = verify_webhook(
        ...     payload=request.body,
        ...     signature=request.headers["X-Webhook-Signature"],
        ...     timestamp=request.headers["X-Webhook-Timestamp"],
        ...     secret="whsec_xxx",
        ... )
        >>> if result.valid:
        ...     handle_event(result.payload)
    """
    # Validate timestamp
    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        return WebhookVerifyFailure(valid=False, error="Invalid timestamp")

    now = int(time.time())
    if abs(now - ts) > max_age:
        return WebhookVerifyFailure(valid=False, error="Timestamp too old")

    # Ensure payload is string
    if isinstance(payload, bytes):
        payload_str = payload.decode("utf-8")
    else:
        payload_str = payload

    # Compute expected signature
    signed_payload = f"{timestamp}.{payload_str}"
    expected = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    # Timing-safe comparison
    if not hmac.compare_digest(expected, signature):
        return WebhookVerifyFailure(valid=False, error="Invalid signature")

    # Parse payload
    try:
        data = json.loads(payload_str)
    except json.JSONDecodeError:
        return WebhookVerifyFailure(valid=False, error="Invalid JSON payload")

    return WebhookVerifySuccess(valid=True, payload=data)


@dataclass
class InboundWebhookVerifySuccess:
    """Successful inbound webhook verification result."""

    valid: Literal[True]
    payload: dict[str, Any]


@dataclass
class InboundWebhookVerifyFailure:
    """Failed inbound webhook verification result."""

    valid: Literal[False]
    error: str


InboundWebhookVerifyResult = Union[InboundWebhookVerifySuccess, InboundWebhookVerifyFailure]


def verify_inbound_webhook(
    *,
    payload: str | bytes,
    signature: str,
    timestamp: str,
    secret: str,
    max_age: int = 300,
) -> InboundWebhookVerifyResult:
    """
    Verify an inbound email webhook signature from SendPigeon.

    Args:
        payload: Raw request body (string or bytes)
        signature: Value of X-Webhook-Signature header
        timestamp: Value of X-Webhook-Timestamp header
        secret: Your inbound webhook secret
        max_age: Maximum age of webhook in seconds (default: 300 = 5 minutes)

    Returns:
        InboundWebhookVerifyResult with valid=True and payload, or valid=False and error

    Example:
        >>> result = verify_inbound_webhook(
        ...     payload=request.body,
        ...     signature=request.headers["X-Webhook-Signature"],
        ...     timestamp=request.headers["X-Webhook-Timestamp"],
        ...     secret="whsec_xxx",
        ... )
        >>> if result.valid:
        ...     email = result.payload["data"]
        ...     print(f"From: {email['from']}, Subject: {email['subject']}")
    """
    # Same verification logic as regular webhooks
    result = verify_webhook(
        payload=payload,
        signature=signature,
        timestamp=timestamp,
        secret=secret,
        max_age=max_age,
    )

    if isinstance(result, WebhookVerifySuccess):
        return InboundWebhookVerifySuccess(valid=True, payload=result.payload)
    else:
        return InboundWebhookVerifyFailure(valid=False, error=result.error)
