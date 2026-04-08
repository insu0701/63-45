from __future__ import annotations

import httpx

from backend.app.adapters.kiwoom.constants import OAUTH_TOKEN_PATH
from backend.app.adapters.kiwoom.exceptions import KiwoomAuthError, KiwoomConfigurationError
from backend.app.adapters.kiwoom.types import KiwoomToken
from backend.app.core.config import settings


class KiwoomAuthClient:
    def __init__(self) -> None:
        self._cached_token: KiwoomToken | None = None

    def _validate_config(self) -> None:
        if not settings.kiwoom_app_key:
            raise KiwoomConfigurationError("KIWOOM_APP_KEY is missing.")
        if not settings.kiwoom_secret_key:
            raise KiwoomConfigurationError("KIWOOM_SECRET_KEY is missing.")

    def issue_access_token(self) -> KiwoomToken:
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

        body = response.json()

        token = KiwoomToken(
            token=body["token"],
            token_type=body.get("token_type", "Bearer"),
            expires_dt=body.get("expires_dt", ""),
        )
        self._cached_token = token
        return token

    def get_access_token(self, force_refresh: bool = False) -> str:
        if force_refresh or self._cached_token is None:
            self.issue_access_token()

        assert self._cached_token is not None
        return self._cached_token.token