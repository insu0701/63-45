from __future__ import annotations

from decimal import Decimal

from backend.app.adapters.kiwoom.client import KiwoomRestClient
from backend.app.adapters.kiwoom.normalize import normalize_kr_stock_code, parse_price_abs

MARKET_INFO_RESOURCE_PATH = "/api/dostk/stkinfo"
API_ID_STOCK_BASIC = "ka10001"


class KiwoomMarketDataAdapter:
    def __init__(self, client: KiwoomRestClient | None = None) -> None:
        self.client = client or KiwoomRestClient()

    def get_stock_basic_raw(self, symbol: str):
        normalized = normalize_kr_stock_code(symbol)
        return self.client.post_json(
            path=MARKET_INFO_RESOURCE_PATH,
            api_id=API_ID_STOCK_BASIC,
            body={"stk_cd": normalized},
        )

    def get_current_price(self, symbol: str) -> Decimal | None:
        envelope = self.get_stock_basic_raw(symbol)
        body = envelope.body

        if body.get("return_code") != 0:
            return None

        return parse_price_abs(body.get("cur_prc"))