from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import (
    AudienceStats,
    BatchContactResult,
    Contact,
    ContactListResponse,
    ContactStatus,
    Result,
)

if TYPE_CHECKING:
    from .._http import AsyncHttpClient, SyncHttpClient


def _parse_contact(data: dict) -> Contact:
    """Parse API response into Contact."""
    return Contact(
        id=data["id"],
        email=data["email"],
        fields=data.get("fields", {}),
        tags=data.get("tags", []),
        status=data["status"],
        unsubscribed_at=data.get("unsubscribedAt"),
        bounced_at=data.get("bouncedAt"),
        complained_at=data.get("complainedAt"),
        created_at=data["createdAt"],
        updated_at=data["updatedAt"],
    )


def _build_query_params(
    status: ContactStatus | None = None,
    tag: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """Build query string for list endpoint."""
    params = []
    if status:
        params.append(f"status={status}")
    if tag:
        params.append(f"tag={tag}")
    if search:
        params.append(f"search={search}")
    if limit != 50:
        params.append(f"limit={limit}")
    if offset != 0:
        params.append(f"offset={offset}")
    return "?" + "&".join(params) if params else ""


class SyncContacts:
    """Sync contact operations."""

    def __init__(self, http: SyncHttpClient):
        self._http = http

    def list(
        self,
        *,
        status: ContactStatus | None = None,
        tag: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Result[ContactListResponse]:
        """List contacts.

        Args:
            status: Filter by status
            tag: Filter by tag
            search: Search by email
            limit: Maximum number of results (default: 50)
            offset: Offset for pagination (default: 0)
        """
        path = f"/v1/contacts{_build_query_params(status, tag, search, limit, offset)}"
        result = self._http.request("GET", path)
        if result.error:
            return Result(error=result.error)
        return Result(
            data=ContactListResponse(
                data=[_parse_contact(c) for c in result.data["data"]],
                total=result.data["total"],
            )
        )

    def stats(self) -> Result[AudienceStats]:
        """Get audience statistics."""
        result = self._http.request("GET", "/v1/contacts/stats")
        if result.error:
            return Result(error=result.error)
        return Result(
            data=AudienceStats(
                total=result.data["total"],
                active=result.data["active"],
                unsubscribed=result.data["unsubscribed"],
                bounced=result.data["bounced"],
                complained=result.data["complained"],
            )
        )

    def tags(self) -> Result[list[str]]:
        """List unique tags."""
        result = self._http.request("GET", "/v1/contacts/tags")
        if result.error:
            return Result(error=result.error)
        return Result(data=result.data["data"])

    def create(
        self,
        email: str,
        *,
        fields: dict | None = None,
        tags: list[str] | None = None,
    ) -> Result[Contact]:
        """Create a contact.

        Args:
            email: Contact email address
            fields: Custom fields
            tags: Tags for segmentation
        """
        body = {"email": email}
        if fields is not None:
            body["fields"] = fields
        if tags is not None:
            body["tags"] = tags

        result = self._http.request("POST", "/v1/contacts", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_contact(result.data))

    def batch(
        self,
        contacts: list[dict],
    ) -> Result[BatchContactResult]:
        """Batch create/update contacts.

        Args:
            contacts: List of contact dicts with email, fields, tags
        """
        result = self._http.request("POST", "/v1/contacts/batch", {"contacts": contacts})
        if result.error:
            return Result(error=result.error)
        return Result(
            data=BatchContactResult(
                created=result.data["created"],
                updated=result.data["updated"],
                failed=result.data.get("failed", []),
            )
        )

    def get(self, id: str) -> Result[Contact]:
        """Get a contact by ID."""
        result = self._http.request("GET", f"/v1/contacts/{id}")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_contact(result.data))

    def update(
        self,
        id: str,
        *,
        fields: dict | None = None,
        tags: list[str] | None = None,
    ) -> Result[Contact]:
        """Update a contact.

        Args:
            id: Contact ID
            fields: Custom fields
            tags: Tags for segmentation
        """
        body = {}
        if fields is not None:
            body["fields"] = fields
        if tags is not None:
            body["tags"] = tags

        result = self._http.request("PATCH", f"/v1/contacts/{id}", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_contact(result.data))

    def delete(self, id: str) -> Result[None]:
        """Delete a contact."""
        return self._http.request("DELETE", f"/v1/contacts/{id}")

    def unsubscribe(self, id: str) -> Result[Contact]:
        """Unsubscribe a contact."""
        result = self._http.request("POST", f"/v1/contacts/{id}/unsubscribe")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_contact(result.data))

    def resubscribe(self, id: str) -> Result[Contact]:
        """Resubscribe a contact."""
        result = self._http.request("POST", f"/v1/contacts/{id}/resubscribe")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_contact(result.data))


class AsyncContacts:
    """Async contact operations."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def list(
        self,
        *,
        status: ContactStatus | None = None,
        tag: str | None = None,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Result[ContactListResponse]:
        """List contacts."""
        path = f"/v1/contacts{_build_query_params(status, tag, search, limit, offset)}"
        result = await self._http.request("GET", path)
        if result.error:
            return Result(error=result.error)
        return Result(
            data=ContactListResponse(
                data=[_parse_contact(c) for c in result.data["data"]],
                total=result.data["total"],
            )
        )

    async def stats(self) -> Result[AudienceStats]:
        """Get audience statistics."""
        result = await self._http.request("GET", "/v1/contacts/stats")
        if result.error:
            return Result(error=result.error)
        return Result(
            data=AudienceStats(
                total=result.data["total"],
                active=result.data["active"],
                unsubscribed=result.data["unsubscribed"],
                bounced=result.data["bounced"],
                complained=result.data["complained"],
            )
        )

    async def tags(self) -> Result[list[str]]:
        """List unique tags."""
        result = await self._http.request("GET", "/v1/contacts/tags")
        if result.error:
            return Result(error=result.error)
        return Result(data=result.data["data"])

    async def create(
        self,
        email: str,
        *,
        fields: dict | None = None,
        tags: list[str] | None = None,
    ) -> Result[Contact]:
        """Create a contact."""
        body = {"email": email}
        if fields is not None:
            body["fields"] = fields
        if tags is not None:
            body["tags"] = tags

        result = await self._http.request("POST", "/v1/contacts", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_contact(result.data))

    async def batch(self, contacts: list[dict]) -> Result[BatchContactResult]:
        """Batch create/update contacts."""
        result = await self._http.request("POST", "/v1/contacts/batch", {"contacts": contacts})
        if result.error:
            return Result(error=result.error)
        return Result(
            data=BatchContactResult(
                created=result.data["created"],
                updated=result.data["updated"],
                failed=result.data.get("failed", []),
            )
        )

    async def get(self, id: str) -> Result[Contact]:
        """Get a contact by ID."""
        result = await self._http.request("GET", f"/v1/contacts/{id}")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_contact(result.data))

    async def update(
        self,
        id: str,
        *,
        fields: dict | None = None,
        tags: list[str] | None = None,
    ) -> Result[Contact]:
        """Update a contact."""
        body = {}
        if fields is not None:
            body["fields"] = fields
        if tags is not None:
            body["tags"] = tags

        result = await self._http.request("PATCH", f"/v1/contacts/{id}", body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_contact(result.data))

    async def delete(self, id: str) -> Result[None]:
        """Delete a contact."""
        return await self._http.request("DELETE", f"/v1/contacts/{id}")

    async def unsubscribe(self, id: str) -> Result[Contact]:
        """Unsubscribe a contact."""
        result = await self._http.request("POST", f"/v1/contacts/{id}/unsubscribe")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_contact(result.data))

    async def resubscribe(self, id: str) -> Result[Contact]:
        """Resubscribe a contact."""
        result = await self._http.request("POST", f"/v1/contacts/{id}/resubscribe")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_contact(result.data))
