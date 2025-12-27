from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import Result, Template

if TYPE_CHECKING:
    from .._http import AsyncHttpClient, SyncHttpClient


def _parse_template(data: dict) -> Template:
    """Parse API response into Template."""
    return Template(
        id=data["id"],
        name=data["name"],
        subject=data["subject"],
        html=data.get("html"),
        text=data.get("text"),
        variables=data.get("variables", []),
        domain=data.get("domain"),
        created_at=data["createdAt"],
        updated_at=data["updatedAt"],
    )


class SyncTemplates:
    """Sync template operations."""

    def __init__(self, http: SyncHttpClient):
        self._http = http

    def list(self) -> Result[list[Template]]:
        """List all templates."""
        result = self._http.request("GET", "/v1/templates")
        if result.error:
            return Result(error=result.error)
        return Result(data=[_parse_template(t) for t in result.data])

    def get(self, id: str) -> Result[Template]:
        """Get template by ID."""
        result = self._http.request("GET", f"/v1/templates/{id}")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    def create(
        self,
        name: str,
        subject: str,
        html: str | None = None,
        text: str | None = None,
        domain_id: str | None = None,
    ) -> Result[Template]:
        """Create a new template."""
        body = {"name": name, "subject": subject}
        if html:
            body["html"] = html
        if text:
            body["text"] = text
        if domain_id:
            body["domainId"] = domain_id

        result = self._http.request("POST", "/v1/templates", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    def update(
        self,
        id: str,
        name: str | None = None,
        subject: str | None = None,
        html: str | None = None,
        text: str | None = None,
    ) -> Result[Template]:
        """Update a template."""
        body = {}
        if name is not None:
            body["name"] = name
        if subject is not None:
            body["subject"] = subject
        if html is not None:
            body["html"] = html
        if text is not None:
            body["text"] = text

        result = self._http.request("PATCH", f"/v1/templates/{id}", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    def delete(self, id: str) -> Result[None]:
        """Delete a template."""
        return self._http.request("DELETE", f"/v1/templates/{id}")


class AsyncTemplates:
    """Async template operations."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def list(self) -> Result[list[Template]]:
        """List all templates."""
        result = await self._http.request("GET", "/v1/templates")
        if result.error:
            return Result(error=result.error)
        return Result(data=[_parse_template(t) for t in result.data])

    async def get(self, id: str) -> Result[Template]:
        """Get template by ID."""
        result = await self._http.request("GET", f"/v1/templates/{id}")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    async def create(
        self,
        name: str,
        subject: str,
        html: str | None = None,
        text: str | None = None,
        domain_id: str | None = None,
    ) -> Result[Template]:
        """Create a new template."""
        body = {"name": name, "subject": subject}
        if html:
            body["html"] = html
        if text:
            body["text"] = text
        if domain_id:
            body["domainId"] = domain_id

        result = await self._http.request("POST", "/v1/templates", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    async def update(
        self,
        id: str,
        name: str | None = None,
        subject: str | None = None,
        html: str | None = None,
        text: str | None = None,
    ) -> Result[Template]:
        """Update a template."""
        body = {}
        if name is not None:
            body["name"] = name
        if subject is not None:
            body["subject"] = subject
        if html is not None:
            body["html"] = html
        if text is not None:
            body["text"] = text

        result = await self._http.request("PATCH", f"/v1/templates/{id}", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    async def delete(self, id: str) -> Result[None]:
        """Delete a template."""
        return await self._http.request("DELETE", f"/v1/templates/{id}")
