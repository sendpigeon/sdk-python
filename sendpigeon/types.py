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


@dataclass
class BatchEmailResult:
    """Result for a single email in a batch."""

    index: int
    status: Literal["sent", "error"]
    id: str | None = None
    suppressed: list[str] | None = None
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
