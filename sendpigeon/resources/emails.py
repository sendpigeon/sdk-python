from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import EmailDetail, Result

if TYPE_CHECKING:
    from .._http import AsyncHttpClient, SyncHttpClient


def _parse_email_detail(data: dict) -> EmailDetail:
    """Parse API response into EmailDetail."""
    return EmailDetail(
        id=data["id"],
        from_address=data["fromAddress"],
        to_address=data["toAddress"],
        cc_address=data.get("ccAddress"),
        bcc_address=data.get("bccAddress"),
        subject=data["subject"],
        status=data["status"],
        tags=data.get("tags", []),
        metadata=data.get("metadata"),
        created_at=data["createdAt"],
        sent_at=data.get("sentAt"),
        delivered_at=data.get("deliveredAt"),
        bounced_at=data.get("bouncedAt"),
        complained_at=data.get("complainedAt"),
        bounce_type=data.get("bounceType"),
        complaint_type=data.get("complaintType"),
        attachments=data.get("attachments"),
        has_body=data.get("hasBody", False),
    )


class SyncEmails:
    """Sync email operations."""

    def __init__(self, http: SyncHttpClient):
        self._http = http

    def get(self, id: str) -> Result[EmailDetail]:
        """Get email details by ID."""
        result = self._http.request("GET", f"/v1/emails/{id}")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_email_detail(result.data))

    def cancel(self, id: str) -> Result[None]:
        """Cancel a scheduled email."""
        return self._http.request("DELETE", f"/v1/emails/{id}/schedule")


class AsyncEmails:
    """Async email operations."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def get(self, id: str) -> Result[EmailDetail]:
        """Get email details by ID."""
        result = await self._http.request("GET", f"/v1/emails/{id}")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_email_detail(result.data))

    async def cancel(self, id: str) -> Result[None]:
        """Cancel a scheduled email."""
        return await self._http.request("DELETE", f"/v1/emails/{id}/schedule")
