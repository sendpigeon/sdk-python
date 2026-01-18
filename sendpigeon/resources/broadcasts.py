from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import (
    Broadcast,
    BroadcastAnalytics,
    BroadcastListResponse,
    BroadcastRecipient,
    BroadcastStats,
    BroadcastStatus,
    BroadcastTargeting,
    LinkPerformance,
    OpensOverTime,
    RecipientListResponse,
    RecipientStatus,
    Result,
    TestBroadcastResponse,
)

if TYPE_CHECKING:
    from .._http import AsyncHttpClient, SyncHttpClient


def _parse_stats(data: dict) -> BroadcastStats:
    """Parse broadcast stats."""
    return BroadcastStats(
        total_recipients=data.get("totalRecipients", 0),
        sent_count=data.get("sentCount", 0),
        delivered_count=data.get("deliveredCount", 0),
        opened_count=data.get("openedCount", 0),
        clicked_count=data.get("clickedCount", 0),
        bounced_count=data.get("bouncedCount", 0),
        complained_count=data.get("complainedCount", 0),
        unsubscribed_count=data.get("unsubscribedCount", 0),
    )


def _parse_broadcast(data: dict) -> Broadcast:
    """Parse API response into Broadcast."""
    return Broadcast(
        id=data["id"],
        name=data["name"],
        subject=data["subject"],
        preview_text=data.get("previewText"),
        html_content=data.get("htmlContent"),
        content=data.get("content"),
        text_content=data.get("textContent"),
        from_name=data["fromName"],
        from_email=data["fromEmail"],
        reply_to=data.get("replyTo"),
        physical_address=data.get("physicalAddress"),
        tags=data.get("tags", []),
        status=data["status"],
        scheduled_at=data.get("scheduledAt"),
        sent_at=data.get("sentAt"),
        completed_at=data.get("completedAt"),
        stats=_parse_stats(data.get("stats", {})),
        created_at=data["createdAt"],
        updated_at=data["updatedAt"],
    )


def _parse_recipient(data: dict) -> BroadcastRecipient:
    """Parse API response into BroadcastRecipient."""
    return BroadcastRecipient(
        id=data["id"],
        contact_id=data["contactId"],
        email=data["email"],
        status=data["status"],
        sent_at=data.get("sentAt"),
        delivered_at=data.get("deliveredAt"),
        opened_at=data.get("openedAt"),
        clicked_at=data.get("clickedAt"),
        bounced_at=data.get("bouncedAt"),
        complained_at=data.get("complainedAt"),
        unsubscribed_at=data.get("unsubscribedAt"),
        created_at=data["createdAt"],
    )


def _build_list_params(
    status: BroadcastStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """Build query string for list endpoint."""
    params = []
    if status:
        params.append(f"status={status}")
    if limit != 50:
        params.append(f"limit={limit}")
    if offset != 0:
        params.append(f"offset={offset}")
    return "?" + "&".join(params) if params else ""


def _build_recipient_params(
    status: RecipientStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """Build query string for recipients endpoint."""
    params = []
    if status:
        params.append(f"status={status}")
    if limit != 50:
        params.append(f"limit={limit}")
    if offset != 0:
        params.append(f"offset={offset}")
    return "?" + "&".join(params) if params else ""


def _build_targeting_body(
    include_tags: list[str] | None = None,
    exclude_tags: list[str] | None = None,
) -> dict:
    """Build targeting body for send/schedule requests."""
    body = {}
    if include_tags:
        body["includeTags"] = include_tags
    if exclude_tags:
        body["excludeTags"] = exclude_tags
    return body


class SyncBroadcasts:
    """Sync broadcast operations."""

    def __init__(self, http: SyncHttpClient):
        self._http = http

    def list(
        self,
        *,
        status: BroadcastStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Result[BroadcastListResponse]:
        """List broadcasts.

        Args:
            status: Filter by status
            limit: Maximum number of results (default: 50)
            offset: Offset for pagination (default: 0)
        """
        path = f"/v1/broadcasts{_build_list_params(status, limit, offset)}"
        result = self._http.request("GET", path)
        if result.error:
            return Result(error=result.error)
        return Result(
            data=BroadcastListResponse(
                data=[_parse_broadcast(b) for b in result.data["data"]],
                total=result.data["total"],
            )
        )

    def create(
        self,
        *,
        name: str,
        subject: str,
        from_name: str,
        from_email: str,
        preview_text: str | None = None,
        html_content: str | None = None,
        content: dict | None = None,
        text_content: str | None = None,
        reply_to: str | None = None,
        tags: list[str] | None = None,
        broadcast_template_id: str | None = None,
    ) -> Result[Broadcast]:
        """Create a broadcast.

        Args:
            name: Broadcast name
            subject: Email subject
            from_name: Sender name
            from_email: Sender email (must use a verified domain)
            preview_text: Preview text
            html_content: HTML content
            content: Editor JSON content
            text_content: Plain text content
            reply_to: Reply-to email
            tags: Tags for targeting contacts
            broadcast_template_id: Template ID to copy content from
        """
        body = {
            "name": name,
            "subject": subject,
            "fromName": from_name,
            "fromEmail": from_email,
        }
        if preview_text is not None:
            body["previewText"] = preview_text
        if html_content is not None:
            body["htmlContent"] = html_content
        if content is not None:
            body["content"] = content
        if text_content is not None:
            body["textContent"] = text_content
        if reply_to is not None:
            body["replyTo"] = reply_to
        if tags is not None:
            body["tags"] = tags
        if broadcast_template_id is not None:
            body["broadcastTemplateId"] = broadcast_template_id

        result = self._http.request("POST", "/v1/broadcasts", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    def get(self, id: str) -> Result[Broadcast]:
        """Get a broadcast by ID."""
        result = self._http.request("GET", f"/v1/broadcasts/{id}")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    def update(
        self,
        id: str,
        *,
        name: str | None = None,
        subject: str | None = None,
        preview_text: str | None = None,
        html_content: str | None = None,
        content: dict | None = None,
        text_content: str | None = None,
        from_name: str | None = None,
        from_email: str | None = None,
        reply_to: str | None = None,
        tags: list[str] | None = None,
    ) -> Result[Broadcast]:
        """Update a broadcast (draft only)."""
        body = {}
        if name is not None:
            body["name"] = name
        if subject is not None:
            body["subject"] = subject
        if preview_text is not None:
            body["previewText"] = preview_text
        if html_content is not None:
            body["htmlContent"] = html_content
        if content is not None:
            body["content"] = content
        if text_content is not None:
            body["textContent"] = text_content
        if from_name is not None:
            body["fromName"] = from_name
        if from_email is not None:
            body["fromEmail"] = from_email
        if reply_to is not None:
            body["replyTo"] = reply_to
        if tags is not None:
            body["tags"] = tags

        result = self._http.request("PATCH", f"/v1/broadcasts/{id}", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    def delete(self, id: str) -> Result[None]:
        """Delete a broadcast (draft only)."""
        return self._http.request("DELETE", f"/v1/broadcasts/{id}")

    def duplicate(self, id: str) -> Result[Broadcast]:
        """Duplicate a broadcast."""
        result = self._http.request("POST", f"/v1/broadcasts/{id}/duplicate")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    def recipients(
        self,
        id: str,
        *,
        status: RecipientStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Result[RecipientListResponse]:
        """List recipients of a broadcast."""
        path = f"/v1/broadcasts/{id}/recipients{_build_recipient_params(status, limit, offset)}"
        result = self._http.request("GET", path)
        if result.error:
            return Result(error=result.error)
        return Result(
            data=RecipientListResponse(
                data=[_parse_recipient(r) for r in result.data["data"]],
                total=result.data["total"],
            )
        )

    def send(
        self,
        id: str,
        *,
        include_tags: list[str] | None = None,
        exclude_tags: list[str] | None = None,
    ) -> Result[Broadcast]:
        """Send a broadcast immediately.

        Args:
            id: Broadcast ID
            include_tags: Only send to contacts with ANY of these tags
            exclude_tags: Exclude contacts with ANY of these tags
        """
        body = _build_targeting_body(include_tags, exclude_tags)
        result = self._http.request("POST", f"/v1/broadcasts/{id}/send", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    def schedule(
        self,
        id: str,
        *,
        scheduled_at: str,
        include_tags: list[str] | None = None,
        exclude_tags: list[str] | None = None,
    ) -> Result[Broadcast]:
        """Schedule a broadcast.

        Args:
            id: Broadcast ID
            scheduled_at: ISO 8601 datetime
            include_tags: Only send to contacts with ANY of these tags
            exclude_tags: Exclude contacts with ANY of these tags
        """
        body = {"scheduledAt": scheduled_at, **_build_targeting_body(include_tags, exclude_tags)}
        result = self._http.request("POST", f"/v1/broadcasts/{id}/schedule", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    def cancel(self, id: str) -> Result[Broadcast]:
        """Cancel a scheduled broadcast."""
        result = self._http.request("POST", f"/v1/broadcasts/{id}/cancel")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    def test(self, id: str, *, email: str) -> Result[TestBroadcastResponse]:
        """Send a test email.

        Args:
            id: Broadcast ID
            email: Email address to send test to
        """
        result = self._http.request("POST", f"/v1/broadcasts/{id}/test", {"email": email})
        if result.error:
            return Result(error=result.error)
        return Result(
            data=TestBroadcastResponse(
                success=result.data["success"],
                message=result.data["message"],
            )
        )

    def analytics(self, id: str) -> Result[BroadcastAnalytics]:
        """Get broadcast analytics."""
        result = self._http.request("GET", f"/v1/broadcasts/{id}/analytics")
        if result.error:
            return Result(error=result.error)
        return Result(
            data=BroadcastAnalytics(
                opens_over_time=[
                    OpensOverTime(hour=o["hour"], opens=o["opens"])
                    for o in result.data.get("opensOverTime", [])
                ],
                link_performance=[
                    LinkPerformance(
                        url=l["url"], clicks=l["clicks"], unique_clicks=l["uniqueClicks"]
                    )
                    for l in result.data.get("linkPerformance", [])
                ],
            )
        )


class AsyncBroadcasts:
    """Async broadcast operations."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def list(
        self,
        *,
        status: BroadcastStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Result[BroadcastListResponse]:
        """List broadcasts."""
        path = f"/v1/broadcasts{_build_list_params(status, limit, offset)}"
        result = await self._http.request("GET", path)
        if result.error:
            return Result(error=result.error)
        return Result(
            data=BroadcastListResponse(
                data=[_parse_broadcast(b) for b in result.data["data"]],
                total=result.data["total"],
            )
        )

    async def create(
        self,
        *,
        name: str,
        subject: str,
        from_name: str,
        from_email: str,
        preview_text: str | None = None,
        html_content: str | None = None,
        content: dict | None = None,
        text_content: str | None = None,
        reply_to: str | None = None,
        tags: list[str] | None = None,
        broadcast_template_id: str | None = None,
    ) -> Result[Broadcast]:
        """Create a broadcast."""
        body = {
            "name": name,
            "subject": subject,
            "fromName": from_name,
            "fromEmail": from_email,
        }
        if preview_text is not None:
            body["previewText"] = preview_text
        if html_content is not None:
            body["htmlContent"] = html_content
        if content is not None:
            body["content"] = content
        if text_content is not None:
            body["textContent"] = text_content
        if reply_to is not None:
            body["replyTo"] = reply_to
        if tags is not None:
            body["tags"] = tags
        if broadcast_template_id is not None:
            body["broadcastTemplateId"] = broadcast_template_id

        result = await self._http.request("POST", "/v1/broadcasts", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    async def get(self, id: str) -> Result[Broadcast]:
        """Get a broadcast by ID."""
        result = await self._http.request("GET", f"/v1/broadcasts/{id}")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    async def update(
        self,
        id: str,
        *,
        name: str | None = None,
        subject: str | None = None,
        preview_text: str | None = None,
        html_content: str | None = None,
        content: dict | None = None,
        text_content: str | None = None,
        from_name: str | None = None,
        from_email: str | None = None,
        reply_to: str | None = None,
        tags: list[str] | None = None,
    ) -> Result[Broadcast]:
        """Update a broadcast (draft only)."""
        body = {}
        if name is not None:
            body["name"] = name
        if subject is not None:
            body["subject"] = subject
        if preview_text is not None:
            body["previewText"] = preview_text
        if html_content is not None:
            body["htmlContent"] = html_content
        if content is not None:
            body["content"] = content
        if text_content is not None:
            body["textContent"] = text_content
        if from_name is not None:
            body["fromName"] = from_name
        if from_email is not None:
            body["fromEmail"] = from_email
        if reply_to is not None:
            body["replyTo"] = reply_to
        if tags is not None:
            body["tags"] = tags

        result = await self._http.request("PATCH", f"/v1/broadcasts/{id}", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    async def delete(self, id: str) -> Result[None]:
        """Delete a broadcast (draft only)."""
        return await self._http.request("DELETE", f"/v1/broadcasts/{id}")

    async def duplicate(self, id: str) -> Result[Broadcast]:
        """Duplicate a broadcast."""
        result = await self._http.request("POST", f"/v1/broadcasts/{id}/duplicate")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    async def recipients(
        self,
        id: str,
        *,
        status: RecipientStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Result[RecipientListResponse]:
        """List recipients of a broadcast."""
        path = f"/v1/broadcasts/{id}/recipients{_build_recipient_params(status, limit, offset)}"
        result = await self._http.request("GET", path)
        if result.error:
            return Result(error=result.error)
        return Result(
            data=RecipientListResponse(
                data=[_parse_recipient(r) for r in result.data["data"]],
                total=result.data["total"],
            )
        )

    async def send(
        self,
        id: str,
        *,
        include_tags: list[str] | None = None,
        exclude_tags: list[str] | None = None,
    ) -> Result[Broadcast]:
        """Send a broadcast immediately.

        Args:
            id: Broadcast ID
            include_tags: Only send to contacts with ANY of these tags
            exclude_tags: Exclude contacts with ANY of these tags
        """
        body = _build_targeting_body(include_tags, exclude_tags)
        result = await self._http.request("POST", f"/v1/broadcasts/{id}/send", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    async def schedule(
        self,
        id: str,
        *,
        scheduled_at: str,
        include_tags: list[str] | None = None,
        exclude_tags: list[str] | None = None,
    ) -> Result[Broadcast]:
        """Schedule a broadcast.

        Args:
            id: Broadcast ID
            scheduled_at: ISO 8601 datetime
            include_tags: Only send to contacts with ANY of these tags
            exclude_tags: Exclude contacts with ANY of these tags
        """
        body = {"scheduledAt": scheduled_at, **_build_targeting_body(include_tags, exclude_tags)}
        result = await self._http.request("POST", f"/v1/broadcasts/{id}/schedule", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    async def cancel(self, id: str) -> Result[Broadcast]:
        """Cancel a scheduled broadcast."""
        result = await self._http.request("POST", f"/v1/broadcasts/{id}/cancel")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_broadcast(result.data))

    async def test(self, id: str, *, email: str) -> Result[TestBroadcastResponse]:
        """Send a test email."""
        result = await self._http.request("POST", f"/v1/broadcasts/{id}/test", {"email": email})
        if result.error:
            return Result(error=result.error)
        return Result(
            data=TestBroadcastResponse(
                success=result.data["success"],
                message=result.data["message"],
            )
        )

    async def analytics(self, id: str) -> Result[BroadcastAnalytics]:
        """Get broadcast analytics."""
        result = await self._http.request("GET", f"/v1/broadcasts/{id}/analytics")
        if result.error:
            return Result(error=result.error)
        return Result(
            data=BroadcastAnalytics(
                opens_over_time=[
                    OpensOverTime(hour=o["hour"], opens=o["opens"])
                    for o in result.data.get("opensOverTime", [])
                ],
                link_performance=[
                    LinkPerformance(
                        url=l["url"], clicks=l["clicks"], unique_clicks=l["uniqueClicks"]
                    )
                    for l in result.data.get("linkPerformance", [])
                ],
            )
        )
