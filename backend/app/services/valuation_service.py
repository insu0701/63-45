from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.models import CashBalanceSnapshot, HoldingSnapshot
from backend.app.services.active_snapshot_service import ActiveSnapshotService


@dataclass
class PositionValuation:
    symbol: str
    security_name: str
    sleeve: str
    country: str
    currency: str
    market_value_base: Decimal
    cost_basis_base: Decimal
    unrealized_pnl_base: Decimal
    unrealized_return_pct: Decimal
    quantity: Decimal


@dataclass
class CashValuation:
    currency: str
    amount_native: Decimal
    amount_base: Decimal


@dataclass
class PortfolioValuationSummary:
    total_equity_value_base: Decimal
    total_cash_base: Decimal
    total_nav_base: Decimal
    total_unrealized_pnl_base: Decimal
    total_unrealized_return_pct: Decimal


class ValuationService:
    def __init__(self, db: Session):
        self.db = db
        self.active_snapshot_service = ActiveSnapshotService(db)

    def _latest_snapshot_time_for_holdings(self):
        return self.active_snapshot_service.get_active_holdings_snapshot_time()

    def _latest_snapshot_time_for_cash(self):
        return self.active_snapshot_service.get_active_cash_snapshot_time()
    
    def get_latest_holdings_snapshot_time(self):
        return self._latest_snapshot_time_for_holdings()

    def get_latest_cash_snapshot_time(self):
        return self._latest_snapshot_time_for_cash()

    def get_latest_holdings(self) -> list[HoldingSnapshot]:
        snapshot_time = self._latest_snapshot_time_for_holdings()
        if snapshot_time is None:
            return []

        stmt = (
            select(HoldingSnapshot)
            .where(HoldingSnapshot.snapshot_time == snapshot_time)
            .order_by(HoldingSnapshot.market_value_base.desc(), HoldingSnapshot.symbol.asc())
        )
        return list(self.db.scalars(stmt).all())

    def get_latest_cash_balances(self) -> list[CashBalanceSnapshot]:
        snapshot_time = self._latest_snapshot_time_for_cash()
        if snapshot_time is None:
            return []

        stmt = (
            select(CashBalanceSnapshot)
            .where(CashBalanceSnapshot.snapshot_time == snapshot_time)
            .order_by(CashBalanceSnapshot.currency.asc())
        )
        return list(self.db.scalars(stmt).all())

    def get_position_valuations(self) -> list[PositionValuation]:
        rows = self.get_latest_holdings()
        result: list[PositionValuation] = []

        for row in rows:
            market_value_base = Decimal(row.market_value_base or 0)
            cost_basis_base = Decimal(row.cost_basis_base or 0)
            unrealized_pnl_base = Decimal(row.unrealized_pnl_base or 0)

            if cost_basis_base == 0:
                unrealized_return_pct = Decimal("0")
            else:
                unrealized_return_pct = unrealized_pnl_base / cost_basis_base

            result.append(
                PositionValuation(
                    symbol=row.symbol,
                    security_name=row.security_name,
                    sleeve=row.sleeve,
                    country=row.country,
                    currency=row.currency,
                    market_value_base=market_value_base,
                    cost_basis_base=cost_basis_base,
                    unrealized_pnl_base=unrealized_pnl_base,
                    unrealized_return_pct=unrealized_return_pct,
                    quantity=Decimal(row.quantity or 0),
                )
            )

        return result

    def get_cash_valuations(self) -> list[CashValuation]:
        rows = self.get_latest_cash_balances()
        result: list[CashValuation] = []

        for row in rows:
            result.append(
                CashValuation(
                    currency=row.currency,
                    amount_native=Decimal(row.amount_native or 0),
                    amount_base=Decimal(row.amount_base or 0),
                )
            )

        return result

    def get_portfolio_summary(self) -> PortfolioValuationSummary:
        positions = self.get_position_valuations()
        cash_rows = self.get_cash_valuations()

        total_equity_value_base = sum((p.market_value_base for p in positions), Decimal("0"))
        total_cash_base = sum((c.amount_base for c in cash_rows), Decimal("0"))
        total_nav_base = total_equity_value_base + total_cash_base

        total_cost_basis_base = sum((p.cost_basis_base for p in positions), Decimal("0"))
        total_unrealized_pnl_base = sum((p.unrealized_pnl_base for p in positions), Decimal("0"))

        if total_cost_basis_base == 0:
            total_unrealized_return_pct = Decimal("0")
        else:
            total_unrealized_return_pct = total_unrealized_pnl_base / total_cost_basis_base

        return PortfolioValuationSummary(
            total_equity_value_base=total_equity_value_base,
            total_cash_base=total_cash_base,
            total_nav_base=total_nav_base,
            total_unrealized_pnl_base=total_unrealized_pnl_base,
            total_unrealized_return_pct=total_unrealized_return_pct,
        )