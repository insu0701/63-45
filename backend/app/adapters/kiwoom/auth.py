from __future__ import annotations

from datetime import datetime, timedelta
import threading

import httpx

from backend.app.adapters.kiwoom.constants import OAUTH_TOKEN_PATH
from backend.app.adapters.kiwoom.exceptions import (
    KiwoomAuthError,
    KiwoomConfigurationError,
)
from backend.app.adapters.kiwoom.types import KiwoomToken
from backend.app.core.config import settings


_TOKEN_CACHE: KiwoomToken | None = None
_TOKEN_LOCK = threading.Lock()


def _parse_kiwoom_expires_dt(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None

    try:
        # Kiwoom format example: 20260409165958
        return datetime.strptime(value, "%Y%m%d%H%M%S")
    except ValueError:
        return None


def _is_token_usable(token: KiwoomToken | None) -> bool:
    if token is None:
        return False

    expires_at = _parse_kiwoom_expires_dt(token.expires_dt)
    if expires_at is None:
        return False

    # Refresh a little early
    return datetime.now() < (expires_at - timedelta(minutes=1))


class KiwoomAuthClient:
    def __init__(self) -> None:
        self._cached_token: KiwoomToken | None = None

    def _validate_config(self) -> None:
        if not settings.kiwoom_app_key:
            raise KiwoomConfigurationError("KIWOOM_APP_KEY is missing.")
        if not settings.kiwoom_secret_key:
            raise KiwoomConfigurationError("KIWOOM_SECRET_KEY is missing.")

    def issue_access_token(self) -> KiwoomToken:
        global _TOKEN_CACHE

        self._validate_config()

        url = f"{settings.kiwoom_active_base_url}{OAUTH_TOKEN_PATH}"
        payload = {
            "grant_type": "client_credentials",
            "appkey": settings.kiwoom_app_key,
            "secretkey": settings.kiwoom_secret_key,
        }

        try:
            response = httpx.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json;charset=UTF-8"},
                timeout=settings.kiwoom_timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise KiwoomAuthError(f"Failed to issue Kiwoom access token: {exc}") from exc

        try:
            body = response.json()
        except ValueError as exc:
            raise KiwoomAuthError(
                f"Kiwoom token endpoint returned non-JSON response: {response.text}"
            ) from exc

        if "token" not in body:
            raise KiwoomAuthError(
                f"Kiwoom token response missing 'token'. Response body: {body}"
            )

        token = KiwoomToken(
            token=body["token"],
            token_type=body.get("token_type", "Bearer"),
            expires_dt=body.get("expires_dt", ""),
        )

        self._cached_token = token
        _TOKEN_CACHE = token
        return token

    def get_access_token(self, force_refresh: bool = False) -> str:
        global _TOKEN_CACHE

        with _TOKEN_LOCK:
            if not force_refresh:
                if _is_token_usable(self._cached_token):
                    return self._cached_token.token

                if _is_token_usable(_TOKEN_CACHE):
                    self._cached_token = _TOKEN_CACHE
                    return _TOKEN_CACHE.token

            token = self.issue_access_token()
            return token.token