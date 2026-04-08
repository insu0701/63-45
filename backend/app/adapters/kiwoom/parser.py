from __future__ import annotations

from typing import Any


def parse_account_numbers(payload: dict[str, Any]) -> list[str]:
    raw = payload.get("acctNo")

    if raw is None:
        return []

    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]

    if isinstance(raw, str):
        normalized = raw.replace(";", ",").replace("|", ",")
        return [part.strip() for part in normalized.split(",") if part.strip()]

    value = str(raw).strip()
    return [value] if value else []


def summarize_payload_shape(payload: dict[str, Any]) -> dict[str, str]:
    return {key: type(value).__name__ for key, value in payload.items()}