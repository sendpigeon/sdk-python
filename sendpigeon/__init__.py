"""
SendPigeon Python SDK - Transactional Email API

Example:
    >>> from sendpigeon import SendPigeon
    >>> client = SendPigeon("sk_live_xxx")
    >>> result = client.send(
    ...     to="user@example.com",
    ...     subject="Hello",
    ...     html="<p>Hi there!</p>"
    ... )
    >>> if result.ok:
    ...     print(f"Sent: {result.data.id}")

Async Example:
    >>> from sendpigeon import AsyncSendPigeon
    >>> async with AsyncSendPigeon("sk_live_xxx") as client:
    ...     result = await client.send(to="user@example.com", subject="Hi", html="<p>Hello</p>")
"""

from .async_client import AsyncSendPigeon
from .client import SendPigeon
from .errors import SendPigeonError
from .types import (
    ApiKey,
    ApiKeyMode,
    ApiKeyPermission,
    ApiKeyWithSecret,
    AttachmentInput,
    AttachmentMeta,
    BatchEmailInput,
    BatchEmailResult,
    DnsRecord,
    Domain,
    DomainStatus,
    DomainVerificationResult,
    DomainWithDnsRecords,
    EmailDetail,
    EmailStatus,
    Result,
    SendBatchResponse,
    SendEmailResponse,
    Template,
    TrackingDefaults,
    TrackingOptions,
)
from .webhooks import (
    InboundWebhookVerifyFailure,
    InboundWebhookVerifyResult,
    InboundWebhookVerifySuccess,
    WebhookVerifyFailure,
    WebhookVerifyResult,
    WebhookVerifySuccess,
    verify_inbound_webhook,
    verify_webhook,
)

__version__ = "0.4.0"

__all__ = [
    # Clients
    "SendPigeon",
    "AsyncSendPigeon",
    # Errors
    "SendPigeonError",
    # Types
    "Result",
    "EmailStatus",
    "DomainStatus",
    "ApiKeyMode",
    "ApiKeyPermission",
    "AttachmentInput",
    "AttachmentMeta",
    "BatchEmailInput",
    "SendEmailResponse",
    "BatchEmailResult",
    "SendBatchResponse",
    "EmailDetail",
    "Template",
    "DnsRecord",
    "Domain",
    "DomainWithDnsRecords",
    "DomainVerificationResult",
    "ApiKey",
    "ApiKeyWithSecret",
    "TrackingDefaults",
    "TrackingOptions",
    # Webhooks
    "verify_webhook",
    "verify_inbound_webhook",
    "WebhookVerifyResult",
    "WebhookVerifySuccess",
    "WebhookVerifyFailure",
    "InboundWebhookVerifyResult",
    "InboundWebhookVerifySuccess",
    "InboundWebhookVerifyFailure",
]
