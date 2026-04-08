from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class KiwoomToken:
    token: str
    token_type: str
    expires_dt: str


@dataclass
class KiwoomResponseEnvelope:
    body: dict[str, Any]
    status_code: int
    api_id: str | None
    cont_yn: str | None
    next_key: str | None