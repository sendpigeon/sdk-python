"""Shared utilities for sync and async clients."""

from __future__ import annotations

from dataclasses import asdict

from .types import (
    AttachmentInput,
    BatchEmailInput,
    BatchEmailResult,
    Result,
    SendBatchResponse,
    SendEmailResponse,
)


def build_send_body(
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
) -> dict:
    """Build the request body for sending an email."""
    body: dict = {"to": to}

    if from_:
        body["from"] = from_
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

    return body


def _email_to_dict(email: BatchEmailInput | dict) -> dict:
    """Convert a BatchEmailInput or dict to dict format."""
    if isinstance(email, BatchEmailInput):
        return asdict(email)
    return email


def build_batch_emails(emails: list[BatchEmailInput] | list[dict]) -> list[dict]:
    """Convert batch emails to API format."""
    api_emails = []
    for email in emails:
        data = _email_to_dict(email)
        api_email: dict = {}

        if data.get("to") is not None:
            api_email["to"] = data["to"]
        if data.get("from_") is not None:
            api_email["from"] = data["from_"]
        if data.get("subject") is not None:
            api_email["subject"] = data["subject"]
        if data.get("html") is not None:
            api_email["html"] = data["html"]
        if data.get("text") is not None:
            api_email["text"] = data["text"]
        if data.get("cc") is not None:
            api_email["cc"] = data["cc"]
        if data.get("bcc") is not None:
            api_email["bcc"] = data["bcc"]
        if data.get("reply_to") is not None:
            api_email["replyTo"] = data["reply_to"]
        if data.get("template_id") is not None:
            api_email["templateId"] = data["template_id"]
        if data.get("variables") is not None:
            api_email["variables"] = data["variables"]
        if data.get("attachments") is not None:
            api_email["attachments"] = [
                {
                    "filename": a.filename if isinstance(a, AttachmentInput) else a["filename"],
                    "content": a.content if isinstance(a, AttachmentInput) else a.get("content"),
                    "path": a.path if isinstance(a, AttachmentInput) else a.get("path"),
                    "contentType": a.content_type if isinstance(a, AttachmentInput) else a.get("content_type"),
                }
                for a in data["attachments"]
            ]
        if data.get("tags") is not None:
            api_email["tags"] = data["tags"]
        if data.get("metadata") is not None:
            api_email["metadata"] = data["metadata"]
        if data.get("headers") is not None:
            api_email["headers"] = data["headers"]
        if data.get("scheduled_at") is not None:
            api_email["scheduled_at"] = data["scheduled_at"]
        if data.get("idempotency_key") is not None:
            api_email["idempotencyKey"] = data["idempotency_key"]
        api_emails.append(api_email)
    return api_emails


def parse_send_response(data: dict) -> SendEmailResponse:
    """Parse API response into SendEmailResponse."""
    return SendEmailResponse(
        id=data["id"],
        status=data["status"],
        scheduled_at=data.get("scheduled_at"),
        suppressed=data.get("suppressed"),
    )


def parse_batch_response(data: dict) -> SendBatchResponse:
    """Parse API response into SendBatchResponse."""
    batch_results = [
        BatchEmailResult(
            index=r["index"],
            status=r["status"],
            id=r.get("id"),
            suppressed=r.get("suppressed"),
            error=r.get("error"),
        )
        for r in data["data"]
    ]
    return SendBatchResponse(
        data=batch_results,
        summary=data["summary"],
    )
