from __future__ import annotations

from typing import Any

import httpx

from backend.app.adapters.kiwoom.auth import KiwoomAuthClient
from backend.app.adapters.kiwoom.exceptions import KiwoomRequestError
from backend.app.adapters.kiwoom.types import KiwoomResponseEnvelope
from backend.app.core.config import settings


class KiwoomRestClient:
    def __init__(self, auth_client: KiwoomAuthClient | None = None) -> None:
        self.auth_client = auth_client or KiwoomAuthClient()

    def post_json(
        self,
        *,
        path: str,
        api_id: str,
        body: dict[str, Any] | None = None,
        cont_yn: str | None = None,
        next_key: str | None = None,
    ) -> KiwoomResponseEnvelope:
        token = self.auth_client.get_access_token()
        url = f"{settings.kiwoom_active_base_url}{path}"

        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": f"Bearer {token}",
            "api-id": api_id,
        }

        if cont_yn:
            headers["cont-yn"] = cont_yn
        if next_key:
            headers["next-key"] = next_key

        try:
            response = httpx.post(
                url,
                json=body or {},
                headers=headers,
                timeout=settings.kiwoom_timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise KiwoomRequestError(
                f"Kiwoom request failed: status={exc.response.status_code}, "
                f"api_id={api_id}, body={exc.response.text}"
            ) from exc
        except httpx.HTTPError as exc:
            raise KiwoomRequestError(f"Kiwoom request transport error: {exc}") from exc

        response_body = response.json() if response.content else {}

        return KiwoomResponseEnvelope(
            body=response_body,
            status_code=response.status_code,
            api_id=response.headers.get("api-id"),
            cont_yn=response.headers.get("cont-yn"),
            next_key=response.headers.get("next-key"),
        )