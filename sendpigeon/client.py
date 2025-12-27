from __future__ import annotations

from ._http import ClientOptions, SyncHttpClient
from .resources.api_keys import SyncApiKeys
from .resources.domains import SyncDomains
from .resources.emails import SyncEmails
from .resources.templates import SyncTemplates
from .types import (
    AttachmentInput,
    BatchEmailResult,
    Result,
    SendBatchResponse,
    SendEmailResponse,
)


class SendPigeon:
    """
    SendPigeon SDK client for sending transactional emails.

    Example:
        >>> client = SendPigeon("sk_live_xxx")
        >>> result = client.send(
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
        Initialize the SendPigeon client.

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

        self._http = SyncHttpClient(api_key, options)
        self.emails = SyncEmails(self._http)
        self.templates = SyncTemplates(self._http)
        self.domains = SyncDomains(self._http)
        self.api_keys = SyncApiKeys(self._http)

    def close(self) -> None:
        """Close the HTTP client."""
        self._http.close()

    def __enter__(self) -> SendPigeon:
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def send(
        self,
        *,
        to: str | list[str],
        subject: str | None = None,
        html: str | None = None,
        text: str | None = None,
        from_address: str | None = None,
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
    ) -> Result[SendEmailResponse]:
        """
        Send a transactional email.

        Args:
            to: Recipient email address(es)
            subject: Email subject (required unless using template_id)
            html: HTML body content
            text: Plain text body content
            from_address: Sender email (defaults to verified domain)
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

        Returns:
            Result containing SendEmailResponse or error
        """
        body: dict = {"to": to}

        if from_address:
            body["from"] = from_address
        if subject:
            body["subject"] = subject
        if html:
            body["html"] = html
        if text:
            body["text"] = text
        if cc:
            body["cc"] = cc
        if bcc:
            body["bcc"] = bcc
        if reply_to:
            body["replyTo"] = reply_to
        if template_id:
            body["templateId"] = template_id
        if variables:
            body["variables"] = variables
        if attachments:
            body["attachments"] = [
                {
                    "filename": a.filename,
                    "content": a.content,
                    "path": a.path,
                    "contentType": a.content_type,
                }
                for a in attachments
            ]
        if tags:
            body["tags"] = tags
        if metadata:
            body["metadata"] = metadata
        if headers:
            body["headers"] = headers
        if scheduled_at:
            body["scheduled_at"] = scheduled_at

        request_headers = {}
        if idempotency_key:
            request_headers["Idempotency-Key"] = idempotency_key

        result = self._http.request(
            "POST",
            "/v1/emails",
            body=body,
            headers=request_headers if request_headers else None,
        )

        if result.error:
            return Result(error=result.error)

        return Result(
            data=SendEmailResponse(
                id=result.data["id"],
                status=result.data["status"],
                scheduled_at=result.data.get("scheduled_at"),
                suppressed=result.data.get("suppressed"),
            )
        )

    def send_batch(
        self,
        emails: list[dict],
    ) -> Result[SendBatchResponse]:
        """
        Send multiple emails in a single request (max 100).

        Args:
            emails: List of email objects, each with same fields as send()

        Returns:
            Result containing SendBatchResponse with per-email results
        """
        # Convert to API format
        api_emails = []
        for email in emails:
            api_email: dict = {}
            if "to" in email:
                api_email["to"] = email["to"]
            if "from_address" in email:
                api_email["from"] = email["from_address"]
            if "subject" in email:
                api_email["subject"] = email["subject"]
            if "html" in email:
                api_email["html"] = email["html"]
            if "text" in email:
                api_email["text"] = email["text"]
            if "cc" in email:
                api_email["cc"] = email["cc"]
            if "bcc" in email:
                api_email["bcc"] = email["bcc"]
            if "reply_to" in email:
                api_email["replyTo"] = email["reply_to"]
            if "template_id" in email:
                api_email["templateId"] = email["template_id"]
            if "variables" in email:
                api_email["variables"] = email["variables"]
            if "tags" in email:
                api_email["tags"] = email["tags"]
            if "metadata" in email:
                api_email["metadata"] = email["metadata"]
            if "headers" in email:
                api_email["headers"] = email["headers"]
            if "scheduled_at" in email:
                api_email["scheduled_at"] = email["scheduled_at"]
            if "idempotency_key" in email:
                api_email["idempotencyKey"] = email["idempotency_key"]
            api_emails.append(api_email)

        result = self._http.request("POST", "/v1/emails/batch", body={"emails": api_emails})

        if result.error:
            return Result(error=result.error)

        batch_results = [
            BatchEmailResult(
                index=r["index"],
                status=r["status"],
                id=r.get("id"),
                suppressed=r.get("suppressed"),
                error=r.get("error"),
            )
            for r in result.data["data"]
        ]

        return Result(
            data=SendBatchResponse(
                data=batch_results,
                summary=result.data["summary"],
            )
        )
