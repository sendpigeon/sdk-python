from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, Literal, TypeVar

from .errors import SendPigeonError

T = TypeVar("T")


@dataclass
class Result(Generic[T]):
    """Result wrapper for API responses. Either data or error is set, never both."""

    data: T | None = None
    error: SendPigeonError | None = None

    def unwrap(self) -> T:
        """Return data or raise error. Useful for quick scripts."""
        if self.error:
            raise self.error
        if self.data is None:
            raise ValueError("Result has no data")
        return self.data

    @property
    def ok(self) -> bool:
        """True if request succeeded."""
        return self.error is None


EmailStatus = Literal[
    "scheduled", "cancelled", "pending", "sent", "delivered", "bounced", "complained", "failed"
]
DomainStatus = Literal["pending", "verified", "temporary_failure", "failed"]
ApiKeyMode = Literal["live", "test"]
ApiKeyPermission = Literal["full_access", "sending"]
TemplateStatus = Literal["draft", "published"]
TemplateVariableType = Literal["string", "number", "boolean"]


@dataclass
class TrackingOptions:
    """Per-email tracking options. Tracking is opt-in per email."""

    opens: bool | None = None
    clicks: bool | None = None


@dataclass
class AttachmentInput:
    """Attachment for sending email."""

    filename: str
    content: str | None = None
    path: str | None = None
    content_type: str | None = None


@dataclass
class BatchEmailInput:
    """Input for a single email in a batch send."""

    to: str | list[str]
    subject: str | None = None
    html: str | None = None
    text: str | None = None
    from_: str | None = None
    cc: str | list[str] | None = None
    bcc: str | list[str] | None = None
    reply_to: str | None = None
    template_id: str | None = None
    variables: dict[str, str] | None = None
    attachments: list[AttachmentInput] | None = None
    tags: list[str] | None = None
    metadata: dict[str, str] | None = None
    headers: dict[str, str] | None = None
    scheduled_at: str | None = None
    idempotency_key: str | None = None
    tracking: TrackingOptions | None = None


@dataclass
class AttachmentMeta:
    """Attachment metadata returned from API."""

    filename: str
    size: int
    content_type: str


@dataclass
class SendEmailResponse:
    """Response from sending an email."""

    id: str
    status: EmailStatus
    scheduled_at: str | None = None
    suppressed: list[str] | None = None
    warnings: list[str] | None = None


@dataclass
class BatchEmailResult:
    """Result for a single email in a batch."""

    index: int
    status: Literal["sent", "error"]
    id: str | None = None
    suppressed: list[str] | None = None
    warnings: list[str] | None = None
    error: dict | None = None


@dataclass
class SendBatchResponse:
    """Response from sending batch emails."""

    data: list[BatchEmailResult]
    summary: dict


@dataclass
class EmailDetail:
    """Detailed email information."""

    id: str
    from_address: str
    to_address: str
    subject: str
    status: EmailStatus
    created_at: str
    cc_address: str | None = None
    bcc_address: str | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict | None = None
    sent_at: str | None = None
    delivered_at: str | None = None
    bounced_at: str | None = None
    complained_at: str | None = None
    bounce_type: str | None = None
    complaint_type: str | None = None
    attachments: list[AttachmentMeta] | None = None
    has_body: bool = False


@dataclass
class TemplateVariable:
    """Typed variable for email templates."""

    key: str
    type: TemplateVariableType
    fallback_value: str | None = None


@dataclass
class Template:
    """Email template."""

    id: str
    template_id: str
    subject: str
    variables: list[TemplateVariable]
    status: TemplateStatus
    created_at: str
    updated_at: str
    name: str | None = None
    html: str | None = None
    text: str | None = None
    domain: dict | None = None


@dataclass
class TestTemplateResponse:
    """Response from sending a test email."""

    message: str
    email_id: str


@dataclass
class DnsRecord:
    """DNS record for domain verification."""

    type: str
    name: str
    value: str
    priority: int | None = None


@dataclass
class Domain:
    """Domain information."""

    id: str
    name: str
    status: DomainStatus
    created_at: str
    verified_at: str | None = None
    last_checked_at: str | None = None
    failing_since: str | None = None


@dataclass
class DomainWithDnsRecords(Domain):
    """Domain with DNS records for setup."""

    dns_records: list[DnsRecord] = field(default_factory=list)


@dataclass
class DomainVerificationResult:
    """Result of domain verification."""

    verified: bool
    status: DomainStatus
    dns_records: list[DnsRecord] = field(default_factory=list)


@dataclass
class ApiKey:
    """API key information (without secret)."""

    id: str
    name: str
    key_prefix: str
    mode: ApiKeyMode
    permission: ApiKeyPermission
    created_at: str
    last_used_at: str | None = None
    expires_at: str | None = None
    domain: dict | None = None


@dataclass
class ApiKeyWithSecret(ApiKey):
    """API key with secret (only returned on creation)."""

    key: str = ""


SuppressionReason = Literal["hard_bounce", "complaint"]


@dataclass
class Suppression:
    """Suppressed email address."""

    id: str
    email: str
    reason: SuppressionReason
    created_at: str
    source_email_id: str | None = None


@dataclass
class SuppressionListResponse:
    """Response from listing suppressions."""

    data: list[Suppression]
    total: int


@dataclass
class TrackingDefaults:
    """Organization tracking defaults."""

    tracking_enabled: bool
    privacy_mode: bool
    webhook_on_every_open: bool
    webhook_on_every_click: bool


# Contacts
ContactStatus = Literal["ACTIVE", "UNSUBSCRIBED", "BOUNCED", "COMPLAINED"]


@dataclass
class Contact:
    """Contact in broadcast audience."""

    id: str
    email: str
    fields: dict
    tags: list[str]
    status: ContactStatus
    created_at: str
    updated_at: str
    unsubscribed_at: str | None = None
    bounced_at: str | None = None
    complained_at: str | None = None


@dataclass
class ContactListResponse:
    """Response from listing contacts."""

    data: list[Contact]
    total: int


@dataclass
class AudienceStats:
    """Audience statistics."""

    total: int
    active: int
    unsubscribed: int
    bounced: int
    complained: int


@dataclass
class BatchContactResult:
    """Result from batch contact operation."""

    created: int
    updated: int
    failed: list[dict]


# Broadcasts
BroadcastStatus = Literal["DRAFT", "SCHEDULED", "SENDING", "SENT", "CANCELLED", "FAILED"]
RecipientStatus = Literal["pending", "sent", "delivered", "bounced", "complained", "failed"]


@dataclass
class BroadcastStats:
    """Broadcast delivery statistics."""

    total_recipients: int
    sent_count: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    bounced_count: int
    complained_count: int
    unsubscribed_count: int


@dataclass
class Broadcast:
    """Broadcast campaign."""

    id: str
    name: str
    subject: str
    from_name: str
    from_email: str
    tags: list[str]
    status: BroadcastStatus
    stats: BroadcastStats
    created_at: str
    updated_at: str
    preview_text: str | None = None
    html_content: str | None = None
    content: dict | None = None
    text_content: str | None = None
    reply_to: str | None = None
    physical_address: str | None = None
    scheduled_at: str | None = None
    sent_at: str | None = None
    completed_at: str | None = None


@dataclass
class BroadcastListResponse:
    """Response from listing broadcasts."""

    data: list[Broadcast]
    total: int


@dataclass
class BroadcastRecipient:
    """Recipient of a broadcast."""

    id: str
    contact_id: str
    email: str
    status: RecipientStatus
    created_at: str
    sent_at: str | None = None
    delivered_at: str | None = None
    opened_at: str | None = None
    clicked_at: str | None = None
    bounced_at: str | None = None
    complained_at: str | None = None
    unsubscribed_at: str | None = None


@dataclass
class RecipientListResponse:
    """Response from listing recipients."""

    data: list[BroadcastRecipient]
    total: int


@dataclass
class TestBroadcastResponse:
    """Response from sending a test broadcast email."""

    success: bool
    message: str


@dataclass
class OpensOverTime:
    """Opens aggregated by hour."""

    hour: str
    opens: int


@dataclass
class LinkPerformance:
    """Click performance for a link."""

    url: str
    clicks: int
    unique_clicks: int


@dataclass
class BroadcastAnalytics:
    """Broadcast analytics data."""

    opens_over_time: list[OpensOverTime]
    link_performance: list[LinkPerformance]


@dataclass
class BroadcastTargeting:
    """Tag-based targeting for broadcasts."""

    include_tags: list[str] | None = None
    """Only send to contacts with ANY of these tags. Empty = all active contacts."""
    exclude_tags: list[str] | None = None
    """Exclude contacts with ANY of these tags."""
