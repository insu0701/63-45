from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

import yfinance as yf


@dataclass
class YFinancePrice:
    price: Decimal
    price_timestamp: datetime


class YFinancePriceProvider:
    def get_latest_price(self, symbol: str) -> YFinancePrice | None:
        ticker = yf.Ticker(symbol)

        raw_price = None
        timestamp = datetime.now(UTC)

        try:
            fast_info = ticker.fast_info
        except Exception:
            fast_info = None

        if fast_info:
            for key in ("lastPrice", "regularMarketPrice", "previousClose"):
                value = fast_info.get(key)
                if value is not None:
                    raw_price = value
                    break

        if raw_price is None:
            history = ticker.history(
                period="5d",
                interval="1d",
                auto_adjust=False,
                actions=False,
            )
            if history.empty:
                return None

            closes = history["Close"].dropna()
            if closes.empty:
                return None

            raw_price = closes.iloc[-1]

            try:
                index_value = closes.index[-1].to_pydatetime()
                if index_value.tzinfo is None:
                    timestamp = index_value.replace(tzinfo=UTC)
                else:
                    timestamp = index_value.astimezone(UTC)
            except Exception:
                timestamp = datetime.now(UTC)

        price = Decimal(str(raw_price))
        if price <= 0:
            return None

        return YFinancePrice(price=price, price_timestamp=timestamp)