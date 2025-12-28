from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import Result, Template, TemplateVariable, TestTemplateResponse

if TYPE_CHECKING:
    from .._http import AsyncHttpClient, SyncHttpClient


def _parse_variable(data: dict) -> TemplateVariable:
    """Parse API response into TemplateVariable."""
    return TemplateVariable(
        key=data["key"],
        type=data["type"],
        fallback_value=data.get("fallbackValue"),
    )


def _parse_template(data: dict) -> Template:
    """Parse API response into Template."""
    return Template(
        id=data["id"],
        template_id=data["templateId"],
        name=data.get("name"),
        subject=data["subject"],
        html=data.get("html"),
        text=data.get("text"),
        variables=[_parse_variable(v) for v in data.get("variables", [])],
        status=data["status"],
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
        template_id: str,
        subject: str,
        name: str | None = None,
        html: str | None = None,
        text: str | None = None,
        variables: list[dict] | None = None,
        domain_id: str | None = None,
    ) -> Result[Template]:
        """Create a new template."""
        body: dict = {"templateId": template_id, "subject": subject}
        if name:
            body["name"] = name
        if html:
            body["html"] = html
        if text:
            body["text"] = text
        if variables:
            body["variables"] = variables
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
        variables: list[dict] | None = None,
    ) -> Result[Template]:
        """Update a template."""
        body: dict = {}
        if name is not None:
            body["name"] = name
        if subject is not None:
            body["subject"] = subject
        if html is not None:
            body["html"] = html
        if text is not None:
            body["text"] = text
        if variables is not None:
            body["variables"] = variables

        result = self._http.request("PATCH", f"/v1/templates/{id}", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    def delete(self, id: str) -> Result[None]:
        """Delete a template."""
        return self._http.request("DELETE", f"/v1/templates/{id}")

    def publish(self, id: str) -> Result[Template]:
        """Publish a template."""
        result = self._http.request("POST", f"/v1/templates/{id}/publish")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    def unpublish(self, id: str) -> Result[Template]:
        """Unpublish a template."""
        result = self._http.request("POST", f"/v1/templates/{id}/unpublish")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    def test(
        self, id: str, to: str, variables: dict[str, str] | None = None
    ) -> Result[TestTemplateResponse]:
        """Send a test email using the template."""
        body: dict = {"to": to}
        if variables:
            body["variables"] = variables

        result = self._http.request("POST", f"/v1/templates/{id}/test", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(
            data=TestTemplateResponse(
                message=result.data["message"], email_id=result.data["emailId"]
            )
        )


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
        template_id: str,
        subject: str,
        name: str | None = None,
        html: str | None = None,
        text: str | None = None,
        variables: list[dict] | None = None,
        domain_id: str | None = None,
    ) -> Result[Template]:
        """Create a new template."""
        body: dict = {"templateId": template_id, "subject": subject}
        if name:
            body["name"] = name
        if html:
            body["html"] = html
        if text:
            body["text"] = text
        if variables:
            body["variables"] = variables
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
        variables: list[dict] | None = None,
    ) -> Result[Template]:
        """Update a template."""
        body: dict = {}
        if name is not None:
            body["name"] = name
        if subject is not None:
            body["subject"] = subject
        if html is not None:
            body["html"] = html
        if text is not None:
            body["text"] = text
        if variables is not None:
            body["variables"] = variables

        result = await self._http.request("PATCH", f"/v1/templates/{id}", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    async def delete(self, id: str) -> Result[None]:
        """Delete a template."""
        return await self._http.request("DELETE", f"/v1/templates/{id}")

    async def publish(self, id: str) -> Result[Template]:
        """Publish a template."""
        result = await self._http.request("POST", f"/v1/templates/{id}/publish")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    async def unpublish(self, id: str) -> Result[Template]:
        """Unpublish a template."""
        result = await self._http.request("POST", f"/v1/templates/{id}/unpublish")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_template(result.data))

    async def test(
        self, id: str, to: str, variables: dict[str, str] | None = None
    ) -> Result[TestTemplateResponse]:
        """Send a test email using the template."""
        body: dict = {"to": to}
        if variables:
            body["variables"] = variables

        result = await self._http.request("POST", f"/v1/templates/{id}/test", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(
            data=TestTemplateResponse(
                message=result.data["message"], email_id=result.data["emailId"]
            )
        )
