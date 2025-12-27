from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


ErrorCode = Literal["network_error", "api_error", "timeout_error"]


@dataclass
class SendPigeonError(Exception):
    """Error returned by SendPigeon API or SDK."""

    message: str
    code: ErrorCode
    api_code: str | None = None
    status: int | None = None

    def __str__(self) -> str:
        if self.api_code:
            return f"[{self.api_code}] {self.message}"
        return self.message
