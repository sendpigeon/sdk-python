from __future__ import annotations

from ._http import AsyncHttpClient, ClientOptions
from ._shared import build_batch_emails, build_send_body, parse_batch_response, parse_send_response
from .resources.api_keys import AsyncApiKeys
from .resources.broadcasts import AsyncBroadcasts
from .resources.contacts import AsyncContacts
from .resources.domains import AsyncDomains
from .resources.emails import AsyncEmails
from .resources.suppressions import AsyncSuppressions
from .resources.templates import AsyncTemplates
from .resources.tracking import AsyncTracking
from .types import (
    AttachmentInput,
    BatchEmailInput,
    Result,
    SendBatchResponse,
    SendEmailResponse,
    TrackingOptions,
)


class AsyncSendPigeon:
    """
    Async SendPigeon SDK client for sending transactional emails.

    Example:
        >>> client = AsyncSendPigeon("sk_live_xxx")
        >>> result = await client.send(
        ...     to="user@example.com",
        ...     subject="Hello",
        ...     html="<p>Hi there!</p>"
        ... )
        >>> if result.ok:
        ...     print(f"Sent: {result.data.id}")
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        debug: bool = False,
    ):
        """
        Initialize the async SendPigeon client.

        Args:
            api_key: Your SendPigeon API key (sk_live_xxx or sk_test_xxx)
            base_url: Override the API base URL (default: https://api.sendpigeon.dev)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Max retry attempts for failed requests (default: 2, max: 5)
            debug: Enable debug logging
        """
        options = ClientOptions(debug=debug)
        if base_url:
            options.base_url = base_url
        if timeout:
            options.timeout = timeout
        if max_retries is not None:
            options.max_retries = min(max_retries, 5)

        self._http = AsyncHttpClient(api_key, options)
        self.emails = AsyncEmails(self._http)
        self.templates = AsyncTemplates(self._http)
        self.domains = AsyncDomains(self._http)
        self.api_keys = AsyncApiKeys(self._http)
        self.suppressions = AsyncSuppressions(self._http)
        self.tracking = AsyncTracking(self._http)
        self.contacts = AsyncContacts(self._http)
        self.broadcasts = AsyncBroadcasts(self._http)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._http.close()

    async def __aenter__(self) -> AsyncSendPigeon:
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def send(
        self,
        *,
        to: str | list[str],
        subject: str | None = None,
        html: str | None = None,
        text: str | None = None,
        from_: str | None = None,
        cc: str | list[str] | None = None,
        bcc: str | list[str] | None = None,
        reply_to: str | None = None,
        template_id: str | None = None,
        variables: dict[str, str] | None = None,
        attachments: list[AttachmentInput] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        scheduled_at: str | None = None,
        idempotency_key: str | None = None,
        tracking: TrackingOptions | None = None,
    ) -> Result[SendEmailResponse]:
        """
        Send a transactional email.

        Args:
            to: Recipient email address(es)
            subject: Email subject (required unless using template_id)
            html: HTML body content
            text: Plain text body content
            from_: Sender email (defaults to verified domain)
            cc: CC recipient(s)
            bcc: BCC recipient(s)
            reply_to: Reply-to address
            template_id: Template ID to use instead of subject/body
            variables: Variables to substitute in template
            attachments: File attachments
            tags: Tags for filtering (max 5)
            metadata: Custom key-value pairs for webhooks
            headers: Custom email headers
            scheduled_at: ISO datetime to send (max 30 days ahead)
            idempotency_key: Unique key to prevent duplicate sends
            tracking: Per-email tracking options (opens/clicks)

        Returns:
            Result containing SendEmailResponse or error
        """
        body = build_send_body(
            to=to,
            subject=subject,
            html=html,
            text=text,
            from_=from_,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            template_id=template_id,
            variables=variables,
            attachments=attachments,
            tags=tags,
            metadata=metadata,
            headers=headers,
            scheduled_at=scheduled_at,
            tracking=tracking,
        )

        request_headers = {"Idempotency-Key": idempotency_key} if idempotency_key else None

        result = await self._http.request("POST", "/v1/emails", body=body, headers=request_headers)

        if result.error:
            return Result(error=result.error)

        return Result(data=parse_send_response(result.data))

    async def send_batch(
        self,
        emails: list[BatchEmailInput] | list[dict],
    ) -> Result[SendBatchResponse]:
        """
        Send multiple emails in a single request (max 100).

        Args:
            emails: List of BatchEmailInput objects or dicts with send() fields

        Returns:
            Result containing SendBatchResponse with per-email results
        """
        api_emails = build_batch_emails(emails)
        result = await self._http.request("POST", "/v1/emails/batch", body={"emails": api_emails})

        if result.error:
            return Result(error=result.error)

        return Result(data=parse_batch_response(result.data))
