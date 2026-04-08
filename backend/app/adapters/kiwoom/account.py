from __future__ import annotations

from typing import Any

from backend.app.adapters.kiwoom.client import KiwoomRestClient
from backend.app.adapters.kiwoom.constants import (
    ACCOUNT_RESOURCE_PATH,
    API_ID_ACCOUNT_NUMBERS,
    API_ID_CASH,
    API_ID_DAILY_STATUS,
    API_ID_HOLDINGS,
)
from backend.app.adapters.kiwoom.exceptions import KiwoomConfigurationError
from backend.app.adapters.kiwoom.parser import parse_account_numbers
from backend.app.core.config import settings


def build_cash_request_body() -> dict[str, Any]:
    # kt00001 예수금상세현황요청
    # PDF shows required body field: qry_tp
    return {
        "qry_tp": "2",  # 2: 일반조회
    }


def build_holdings_request_body() -> dict[str, Any]:
    # kt00018 계좌평가잔고내역요청
    # PDF shows required body fields: qry_tp, dmst_stex_tp
    return {
        "qry_tp": "1",          # 1: 합산
        "dmst_stex_tp": "KRX",  # 한국거래소
    }


class KiwoomAccountAdapter:
    def __init__(self, client: KiwoomRestClient | None = None) -> None:
        self.client = client or KiwoomRestClient()

    def get_account_numbers_raw(self):
        return self.client.post_json(
            path=ACCOUNT_RESOURCE_PATH,
            api_id=API_ID_ACCOUNT_NUMBERS,
            body={},
        )

    def get_account_numbers(self) -> list[str]:
        envelope = self.get_account_numbers_raw()
        return parse_account_numbers(envelope.body)

    def get_primary_account_no(self) -> str:
        configured = settings.kiwoom_account_no.strip()
        if configured:
            return configured

        account_numbers = self.get_account_numbers()
        if not account_numbers:
            raise KiwoomConfigurationError(
                "No account number found from Kiwoom. Set KIWOOM_ACCOUNT_NO or verify ka00001."
            )
        return account_numbers[0]

    def get_cash_raw(self):
        return self.client.post_json(
            path=ACCOUNT_RESOURCE_PATH,
            api_id=API_ID_CASH,
            body=build_cash_request_body(),
        )

    def get_daily_status_raw(self):
        return self.client.post_json(
            path=ACCOUNT_RESOURCE_PATH,
            api_id=API_ID_DAILY_STATUS,
            body={},
        )

    def get_holdings_raw(self, max_pages: int = 20) -> dict[str, Any]:
        pages: list[dict[str, Any]] = []
        cont_yn: str | None = None
        next_key: str | None = None

        for _ in range(max_pages):
            envelope = self.client.post_json(
                path=ACCOUNT_RESOURCE_PATH,
                api_id=API_ID_HOLDINGS,
                body=build_holdings_request_body(),
                cont_yn=cont_yn,
                next_key=next_key,
            )

            pages.append(
                {
                    "headers": {
                        "api-id": envelope.api_id,
                        "cont-yn": envelope.cont_yn,
                        "next-key": envelope.next_key,
                        "status_code": envelope.status_code,
                    },
                    "body": envelope.body,
                }
            )

            if envelope.cont_yn != "Y" or not envelope.next_key:
                break

            cont_yn = "Y"
            next_key = envelope.next_key

        return {
            "page_count": len(pages),
            "pages": pages,
        }