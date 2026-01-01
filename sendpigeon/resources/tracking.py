from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import Result, TrackingDefaults

if TYPE_CHECKING:
    from .._http import AsyncHttpClient, SyncHttpClient


def _parse_tracking_defaults(data: dict) -> TrackingDefaults:
    """Parse API response into TrackingDefaults."""
    return TrackingDefaults(
        open_tracking_enabled=data["openTrackingEnabled"],
        click_tracking_enabled=data["clickTrackingEnabled"],
        privacy_mode=data["privacyMode"],
        webhook_on_every_open=data["webhookOnEveryOpen"],
        webhook_on_every_click=data["webhookOnEveryClick"],
    )


class SyncTracking:
    """Sync tracking operations."""

    def __init__(self, http: SyncHttpClient):
        self._http = http

    def get_defaults(self) -> Result[TrackingDefaults]:
        """Get organization tracking defaults."""
        result = self._http.request("GET", "/v1/tracking/defaults")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_tracking_defaults(result.data))

    def update_defaults(
        self,
        *,
        open_tracking_enabled: bool | None = None,
        click_tracking_enabled: bool | None = None,
        privacy_mode: bool | None = None,
        webhook_on_every_open: bool | None = None,
        webhook_on_every_click: bool | None = None,
    ) -> Result[TrackingDefaults]:
        """Update organization tracking defaults.

        Args:
            open_tracking_enabled: Track when recipients open emails
            click_tracking_enabled: Track when recipients click links
            privacy_mode: Don't store IP addresses or user agents
            webhook_on_every_open: Send webhook for every open, not just first
            webhook_on_every_click: Send webhook for every click, not just first
        """
        body = {}
        if open_tracking_enabled is not None:
            body["openTrackingEnabled"] = open_tracking_enabled
        if click_tracking_enabled is not None:
            body["clickTrackingEnabled"] = click_tracking_enabled
        if privacy_mode is not None:
            body["privacyMode"] = privacy_mode
        if webhook_on_every_open is not None:
            body["webhookOnEveryOpen"] = webhook_on_every_open
        if webhook_on_every_click is not None:
            body["webhookOnEveryClick"] = webhook_on_every_click

        result = self._http.request("PATCH", "/v1/tracking/defaults", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_tracking_defaults(result.data))


class AsyncTracking:
    """Async tracking operations."""

    def __init__(self, http: AsyncHttpClient):
        self._http = http

    async def get_defaults(self) -> Result[TrackingDefaults]:
        """Get organization tracking defaults."""
        result = await self._http.request("GET", "/v1/tracking/defaults")
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_tracking_defaults(result.data))

    async def update_defaults(
        self,
        *,
        open_tracking_enabled: bool | None = None,
        click_tracking_enabled: bool | None = None,
        privacy_mode: bool | None = None,
        webhook_on_every_open: bool | None = None,
        webhook_on_every_click: bool | None = None,
    ) -> Result[TrackingDefaults]:
        """Update organization tracking defaults.

        Args:
            open_tracking_enabled: Track when recipients open emails
            click_tracking_enabled: Track when recipients click links
            privacy_mode: Don't store IP addresses or user agents
            webhook_on_every_open: Send webhook for every open, not just first
            webhook_on_every_click: Send webhook for every click, not just first
        """
        body = {}
        if open_tracking_enabled is not None:
            body["openTrackingEnabled"] = open_tracking_enabled
        if click_tracking_enabled is not None:
            body["clickTrackingEnabled"] = click_tracking_enabled
        if privacy_mode is not None:
            body["privacyMode"] = privacy_mode
        if webhook_on_every_open is not None:
            body["webhookOnEveryOpen"] = webhook_on_every_open
        if webhook_on_every_click is not None:
            body["webhookOnEveryClick"] = webhook_on_every_click

        result = await self._http.request("PATCH", "/v1/tracking/defaults", body=body)
        if result.error:
            return Result(error=result.error)
        return Result(data=_parse_tracking_defaults(result.data))
