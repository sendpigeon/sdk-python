from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from ..types import Result, Suppression, SuppressionListResponse

if TYPE_CHECKING:
    from .._http import AsyncHttpClient, SyncHttpClient


def _parse_suppression(data: dict) -> Suppression:
    """Parse API response into Suppression."""
    return Suppression(
        id=data["id"],
        email=data["email"],
        reason=data["reason"],
        created_at=data["createdAt"],
        source_email_id=data.get("sourceEmailId"),
    )


class SyncSuppressions:
    """Sync suppression operations."""

    def __init__(self, http: SyncHttpClient):
        self._http = http

    def list(self, *, limit: int = 50, offset: int = 0) -> Result[SuppressionListResponse]:
        """List suppressed email addresses.

        Args:
            limit: Maximum number of results (default: 50)
            offset: Offset for pagination (default: 0)
        """
        params = []
        if limit != 50:
            params.append(f"limit={limit}")
        if offset != 0:
            params.append(f"offset={offset}")

        path = "/v1/suppressions"
        if params:
            path += "?" + "&".join(params)

        result = self._http.request("GET", path)
        if result.error:
            return Result(error=result.error)

        return Result(
            data=SuppressionListResponse(
                data=[_parse_suppression(s) for s in result.data["data"]],
                total=result.data["total"],
            )
        )

    def delete(self, email: str) -> Result[None]:
        """Remove an email from the suppression list.

        Args:
            email: Email address to remove
        """
        return self._http.request("DELETE", f"/v1/suppressions/{quote(email, safe='')}")


class AsyncSuppressions:
    """Async suppression operations."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def list(self, *, limit: int = 50, offset: int = 0) -> Result[SuppressionListResponse]:
        """List suppressed email addresses.

        Args:
            limit: Maximum number of results (default: 50)
            offset: Offset for pagination (default: 0)
        """
        params = []
        if limit != 50:
            params.append(f"limit={limit}")
        if offset != 0:
            params.append(f"offset={offset}")

        path = "/v1/suppressions"
        if params:
            path += "?" + "&".join(params)

        result = await self._http.request("GET", path)
        if result.error:
            return Result(error=result.error)

        return Result(
            data=SuppressionListResponse(
                data=[_parse_suppression(s) for s in result.data["data"]],
                total=result.data["total"],
            )
        )

    async def delete(self, email: str) -> Result[None]:
        """Remove an email from the suppression list.

        Args:
            email: Email address to remove
        """
        return await self._http.request("DELETE", f"/v1/suppressions/{quote(email, safe='')}")
