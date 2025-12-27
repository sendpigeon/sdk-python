from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Literal

import httpx

from .errors import SendPigeonError
from .types import Result

HttpMethod = Literal["GET", "POST", "PATCH", "DELETE"]

DEFAULT_BASE_URL = "https://api.sendpigeon.dev"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 2


@dataclass
class ClientOptions:
    """Options for configuring the HTTP client."""

    base_url: str = DEFAULT_BASE_URL
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    debug: bool = False


def _should_retry(status: int) -> bool:
    """Check if request should be retried based on status code."""
    return status == 429 or status >= 500


def _get_retry_delay(attempt: int, retry_after: str | None) -> float:
    """Calculate delay before next retry attempt."""
    if retry_after:
        try:
            return float(retry_after)
        except ValueError:
            pass
    return min(0.5 * (2**attempt), 8.0)


def _parse_error(response: httpx.Response) -> tuple[str, str | None]:
    """Parse error message and code from response."""
    try:
        body = response.json()
        message = body.get("message", f"Request failed: {response.status_code}")
        api_code = body.get("code")
        return message, api_code
    except Exception:
        return f"Request failed: {response.status_code}", None


class SyncHttpClient:
    """Synchronous HTTP client with retry logic."""

    def __init__(self, api_key: str, options: ClientOptions):
        self.api_key = api_key
        self.options = options
        self._client = httpx.Client(
            base_url=options.base_url,
            timeout=options.timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def request(
        self,
        method: HttpMethod,
        path: str,
        body: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> Result[Any]:
        """Make an HTTP request with retry logic."""
        max_retries = self.options.max_retries

        for attempt in range(max_retries + 1):
            try:
                if self.options.debug:
                    retry_info = f" (retry {attempt})" if attempt > 0 else ""
                    print(f"[sendpigeon] {method} {path}{retry_info}")
                    if body:
                        print(f"[sendpigeon] body: {body}")

                response = self._client.request(
                    method=method,
                    url=path,
                    json=body,
                    headers=headers,
                )

                if response.status_code == 204:
                    return Result(data=None)

                if response.is_success:
                    return Result(data=response.json())

                if _should_retry(response.status_code) and attempt < max_retries:
                    delay = _get_retry_delay(attempt, response.headers.get("Retry-After"))
                    time.sleep(delay)
                    continue

                message, api_code = _parse_error(response)
                return Result(
                    error=SendPigeonError(
                        message=message,
                        code="api_error",
                        api_code=api_code,
                        status=response.status_code,
                    )
                )

            except httpx.TimeoutException:
                if attempt < max_retries:
                    time.sleep(_get_retry_delay(attempt, None))
                    continue
                return Result(
                    error=SendPigeonError(
                        message="Request timed out",
                        code="timeout_error",
                    )
                )

            except httpx.RequestError as e:
                if attempt < max_retries:
                    time.sleep(_get_retry_delay(attempt, None))
                    continue
                return Result(
                    error=SendPigeonError(
                        message=str(e),
                        code="network_error",
                    )
                )

        return Result(
            error=SendPigeonError(
                message="Max retries exceeded",
                code="network_error",
            )
        )


class AsyncHttpClient:
    """Asynchronous HTTP client with retry logic."""

    def __init__(self, api_key: str, options: ClientOptions):
        self.api_key = api_key
        self.options = options
        self._client = httpx.AsyncClient(
            base_url=options.base_url,
            timeout=options.timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def request(
        self,
        method: HttpMethod,
        path: str,
        body: dict | None = None,
        headers: dict[str, str] | None = None,
    ) -> Result[Any]:
        """Make an HTTP request with retry logic."""
        import asyncio

        max_retries = self.options.max_retries

        for attempt in range(max_retries + 1):
            try:
                if self.options.debug:
                    retry_info = f" (retry {attempt})" if attempt > 0 else ""
                    print(f"[sendpigeon] {method} {path}{retry_info}")
                    if body:
                        print(f"[sendpigeon] body: {body}")

                response = await self._client.request(
                    method=method,
                    url=path,
                    json=body,
                    headers=headers,
                )

                if response.status_code == 204:
                    return Result(data=None)

                if response.is_success:
                    return Result(data=response.json())

                if _should_retry(response.status_code) and attempt < max_retries:
                    delay = _get_retry_delay(attempt, response.headers.get("Retry-After"))
                    await asyncio.sleep(delay)
                    continue

                message, api_code = _parse_error(response)
                return Result(
                    error=SendPigeonError(
                        message=message,
                        code="api_error",
                        api_code=api_code,
                        status=response.status_code,
                    )
                )

            except httpx.TimeoutException:
                if attempt < max_retries:
                    await asyncio.sleep(_get_retry_delay(attempt, None))
                    continue
                return Result(
                    error=SendPigeonError(
                        message="Request timed out",
                        code="timeout_error",
                    )
                )

            except httpx.RequestError as e:
                if attempt < max_retries:
                    await asyncio.sleep(_get_retry_delay(attempt, None))
                    continue
                return Result(
                    error=SendPigeonError(
                        message=str(e),
                        code="network_error",
                    )
                )

        return Result(
            error=SendPigeonError(
                message="Max retries exceeded",
                code="network_error",
            )
        )
