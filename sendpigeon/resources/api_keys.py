from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from ..types import ApiKey, ApiKeyMode, ApiKeyPermission, ApiKeyWithSecret, Result

if TYPE_CHECKING:
    from .._http import AsyncHttpClient, SyncHttpClient


def _parse_api_key(data: dict) -> ApiKey:
    """Parse API response into ApiKey."""
    return ApiKey(
        id=data["id"],
        name=data["name"],
        key_prefix=data["keyPrefix"],
        mode=data["mode"],
        permission=data["permission"],
        created_at=data["createdAt"],
        last_used_at=data.get("lastUsedAt"),
        expires_at=data.get("expiresAt"),
        domain=data.get("domain"),
    )


def _parse_api_key_with_secret(data: dict) -> ApiKeyWithSecret:
    """Parse API response into ApiKeyWithSecret."""
    return ApiKeyWithSecret(
        id=data["id"],
        name=data["name"],
        key_prefix=data["keyPrefix"],
        mode=data["mode"],
        permission=data["permission"],
        created_at=data["createdAt"],
        last_used_at=data.get("lastUsedAt"),
        expires_at=data.get("expiresAt"),
        domain=data.get("domain"),
        key=data["key"],
    )


class SyncApiKeys:
    """Sync API key operations."""

    def __init__(self, http: SyncHttpClient):
        self._http = http

    def list(self) -> Result[list[ApiKey]]:
        """List all API keys."""
        result = self._http.request("GET", "/v1/api-keys")
        if result.error:
            return Result(error=result.error)
        return Result(data=[_parse_api_key(k) for k in result.data])

    def create(
        self,
        name: str,
        mode: ApiKeyMode = "live",
        permission: ApiKeyPermission = "full_access",
        domain_id: str | None = None,
        expires_at: str | None = None,
    ) -> Result[ApiKeyWithSecret]:
        """Create a new API key."""
        body: dict = {"name": name, "mode": mode, "permission": permission}
        if domain_id:
            body["domainId"] = domain_id
        if expires_at:
            body["expiresAt"] = expires_at

        result = self._http.request("POST", "/v1/api-keys", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_api_key_with_secret(result.data))

    def delete(self, id: str) -> Result[None]:
        """Delete an API key."""
        return self._http.request("DELETE", f"/v1/api-keys/{id}")


class AsyncApiKeys:
    """Async API key operations."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def list(self) -> Result[list[ApiKey]]:
        """List all API keys."""
        result = await self._http.request("GET", "/v1/api-keys")
        if result.error:
            return Result(error=result.error)
        return Result(data=[_parse_api_key(k) for k in result.data])

    async def create(
        self,
        name: str,
        mode: ApiKeyMode = "live",
        permission: ApiKeyPermission = "full_access",
        domain_id: str | None = None,
        expires_at: str | None = None,
    ) -> Result[ApiKeyWithSecret]:
        """Create a new API key."""
        body: dict = {"name": name, "mode": mode, "permission": permission}
        if domain_id:
            body["domainId"] = domain_id
        if expires_at:
            body["expiresAt"] = expires_at

        result = await self._http.request("POST", "/v1/api-keys", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_api_key_with_secret(result.data))

    async def delete(self, id: str) -> Result[None]:
        """Delete an API key."""
        return await self._http.request("DELETE", f"/v1/api-keys/{id}")
