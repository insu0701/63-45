from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.db.models import HoldingSnapshot
from backend.app.services.valuation_service import ValuationService


@dataclass
class SleeveExposure:
    sleeve: str
    market_value_base: Decimal
    weight_of_total_nav: Decimal
    position_count: int
    unrealized_pnl_base: Decimal


@dataclass
class CountryExposure:
    country: str
    market_value_base: Decimal
    weight_of_total_nav: Decimal


@dataclass
class SectorExposure:
    sector: str
    market_value_base: Decimal
    weight_of_total_nav: Decimal


@dataclass
class CurrencyExposure:
    currency: str
    total_base_value: Decimal
    weight_of_total_nav: Decimal


class ExposureService:
    def __init__(self, db: Session):
        self.db = db
        self.valuation_service = ValuationService(db)

    def _latest_holdings(self) -> list[HoldingSnapshot]:
        return self.valuation_service.get_latest_holdings()

    def _latest_cash(self):
        return self.valuation_service.get_latest_cash_balances()

    def get_sleeve_exposures(self) -> list[SleeveExposure]:
        holdings = self._latest_holdings()
        summary = self.valuation_service.get_portfolio_summary()
        total_nav = summary.total_nav_base or Decimal("0")

        grouped_value = defaultdict(lambda: Decimal("0"))
        grouped_pnl = defaultdict(lambda: Decimal("0"))
        grouped_count = defaultdict(int)

        for row in holdings:
            sleeve = row.sleeve
            grouped_value[sleeve] += Decimal(row.market_value_base or 0)
            grouped_pnl[sleeve] += Decimal(row.unrealized_pnl_base or 0)
            grouped_count[sleeve] += 1

        exposures: list[SleeveExposure] = []
        for sleeve, market_value in grouped_value.items():
            weight = Decimal("0") if total_nav == 0 else market_value / total_nav
            exposures.append(
                SleeveExposure(
                    sleeve=sleeve,
                    market_value_base=market_value,
                    weight_of_total_nav=weight,
                    position_count=grouped_count[sleeve],
                    unrealized_pnl_base=grouped_pnl[sleeve],
                )
            )

        return sorted(exposures, key=lambda x: x.market_value_base, reverse=True)

    def get_country_exposures(self) -> list[CountryExposure]:
        holdings = self._latest_holdings()
        summary = self.valuation_service.get_portfolio_summary()
        total_nav = summary.total_nav_base or Decimal("0")

        grouped = defaultdict(lambda: Decimal("0"))
        for row in holdings:
            grouped[row.country] += Decimal(row.market_value_base or 0)

        exposures: list[CountryExposure] = []
        for country, market_value in grouped.items():
            weight = Decimal("0") if total_nav == 0 else market_value / total_nav
            exposures.append(
                CountryExposure(
                    country=country,
                    market_value_base=market_value,
                    weight_of_total_nav=weight,
                )
            )

        return sorted(exposures, key=lambda x: x.market_value_base, reverse=True)

    def get_sector_exposures(self) -> list[SectorExposure]:
        holdings = self._latest_holdings()
        summary = self.valuation_service.get_portfolio_summary()
        total_nav = summary.total_nav_base or Decimal("0")

        grouped = defaultdict(lambda: Decimal("0"))
        for row in holdings:
            sector = row.sector or "Unknown"
            grouped[sector] += Decimal(row.market_value_base or 0)

        exposures: list[SectorExposure] = []
        for sector, market_value in grouped.items():
            weight = Decimal("0") if total_nav == 0 else market_value / total_nav
            exposures.append(
                SectorExposure(
                    sector=sector,
                    market_value_base=market_value,
                    weight_of_total_nav=weight,
                )
            )

        return sorted(exposures, key=lambda x: x.market_value_base, reverse=True)

    def get_currency_exposures(self) -> list[CurrencyExposure]:
        holdings = self._latest_holdings()
        cash_rows = self._latest_cash()
        summary = self.valuation_service.get_portfolio_summary()
        total_nav = summary.total_nav_base or Decimal("0")

        grouped = defaultdict(lambda: Decimal("0"))

        for row in holdings:
            grouped[row.currency] += Decimal(row.market_value_base or 0)

        for row in cash_rows:
            grouped[row.currency] += Decimal(row.amount_base or 0)

        exposures: list[CurrencyExposure] = []
        for currency, total_base_value in grouped.items():
            weight = Decimal("0") if total_nav == 0 else total_base_value / total_nav
            exposures.append(
                CurrencyExposure(
                    currency=currency,
                    total_base_value=total_base_value,
                    weight_of_total_nav=weight,
                )
            )

        return sorted(exposures, key=lambda x: x.total_base_value, reverse=True)