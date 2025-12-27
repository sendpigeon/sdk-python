from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import DnsRecord, Domain, DomainVerificationResult, DomainWithDnsRecords, Result

if TYPE_CHECKING:
    from .._http import AsyncHttpClient, SyncHttpClient


def _parse_dns_record(data: dict) -> DnsRecord:
    """Parse API response into DnsRecord."""
    return DnsRecord(
        type=data["type"],
        name=data["name"],
        value=data["value"],
        priority=data.get("priority"),
    )


def _parse_domain(data: dict) -> Domain:
    """Parse API response into Domain."""
    return Domain(
        id=data["id"],
        name=data["name"],
        status=data["status"],
        created_at=data["createdAt"],
        verified_at=data.get("verifiedAt"),
        last_checked_at=data.get("lastCheckedAt"),
        failing_since=data.get("failingSince"),
    )


def _parse_domain_with_dns(data: dict) -> DomainWithDnsRecords:
    """Parse API response into DomainWithDnsRecords."""
    return DomainWithDnsRecords(
        id=data["id"],
        name=data["name"],
        status=data["status"],
        created_at=data["createdAt"],
        verified_at=data.get("verifiedAt"),
        last_checked_at=data.get("lastCheckedAt"),
        failing_since=data.get("failingSince"),
        dns_records=[_parse_dns_record(r) for r in data.get("dnsRecords", [])],
    )


def _parse_verification_result(data: dict) -> DomainVerificationResult:
    """Parse API response into DomainVerificationResult."""
    return DomainVerificationResult(
        verified=data["verified"],
        status=data["status"],
        dns_records=[_parse_dns_record(r) for r in data.get("dnsRecords", [])],
    )


class SyncDomains:
    """Sync domain operations."""

    def __init__(self, http: SyncHttpClient):
        self._http = http

    def list(self) -> Result[list[Domain]]:
        """List all domains."""
        result = self._http.request("GET", "/v1/domains")
        if result.error:
            return Result(error=result.error)
        return Result(data=[_parse_domain(d) for d in result.data])

    def get(self, id: str) -> Result[DomainWithDnsRecords]:
        """Get domain by ID with DNS records."""
        result = self._http.request("GET", f"/v1/domains/{id}")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_domain_with_dns(result.data))

    def create(self, name: str) -> Result[DomainWithDnsRecords]:
        """Create a new domain."""
        result = self._http.request("POST", "/v1/domains", body={"name": name})
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_domain_with_dns(result.data))

    def verify(self, id: str) -> Result[DomainVerificationResult]:
        """Verify a domain's DNS records."""
        result = self._http.request("POST", f"/v1/domains/{id}/verify")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_verification_result(result.data))

    def delete(self, id: str) -> Result[None]:
        """Delete a domain."""
        return self._http.request("DELETE", f"/v1/domains/{id}")


class AsyncDomains:
    """Async domain operations."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def list(self) -> Result[list[Domain]]:
        """List all domains."""
        result = await self._http.request("GET", "/v1/domains")
        if result.error:
            return Result(error=result.error)
        return Result(data=[_parse_domain(d) for d in result.data])

    async def get(self, id: str) -> Result[DomainWithDnsRecords]:
        """Get domain by ID with DNS records."""
        result = await self._http.request("GET", f"/v1/domains/{id}")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_domain_with_dns(result.data))

    async def create(self, name: str) -> Result[DomainWithDnsRecords]:
        """Create a new domain."""
        result = await self._http.request("POST", "/v1/domains", body={"name": name})
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_domain_with_dns(result.data))

    async def verify(self, id: str) -> Result[DomainVerificationResult]:
        """Verify a domain's DNS records."""
        result = await self._http.request("POST", f"/v1/domains/{id}/verify")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_verification_result(result.data))

    async def delete(self, id: str) -> Result[None]:
        """Delete a domain."""
        return await self._http.request("DELETE", f"/v1/domains/{id}")
