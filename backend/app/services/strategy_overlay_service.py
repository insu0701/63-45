from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models import DailyDecisionLog, StrategySnapshot
from backend.app.services.valuation_service import ValuationService


@dataclass
class OverlayRow:
    symbol: str
    security_name: str
    sleeve: str
    market: str
    country: str
    current_market_value_base: Decimal
    current_weight_of_nav: Decimal
    strategy_state: str | None
    target_state: str | None
    target_weight: Decimal | None
    target_dollars: Decimal | None
    actual_position_dollars: Decimal | None
    actual_vs_target_delta: Decimal | None
    eligibility_status: str | None
    buy_list_status: str | None
    reason_code: str | None
    as_of_date: date | None


class StrategyOverlayService:
    def __init__(self, db: Session):
        self.db = db
        self.valuation = ValuationService(db)

    def _latest_strategy_date(self) -> date | None:
        return self.db.scalar(select(func.max(StrategySnapshot.as_of_date)))

    def _infer_market(self, sleeve: str, overlay: StrategySnapshot | None) -> str:
        if overlay is not None and overlay.market:
            return overlay.market
        if sleeve == "KR":
            return "KRX"
        if sleeve == "US":
            return "US"
        return "UNKNOWN"

    def _infer_country(self, sleeve: str, overlay: StrategySnapshot | None) -> str:
        if overlay is not None and overlay.country:
            return overlay.country
        if sleeve in {"KR", "US"}:
            return sleeve
        return "UNKNOWN"

    def get_overlay_rows(self, sleeve: str | None = None) -> list[OverlayRow]:
        latest_date = self._latest_strategy_date()
        positions = self.valuation.get_position_valuations()
        summary = self.valuation.get_portfolio_summary()

        total_nav = summary.total_nav_base or Decimal("0")

        overlay_map: dict[tuple[str, str], StrategySnapshot] = {}
        if latest_date is not None:
            stmt = select(StrategySnapshot).where(StrategySnapshot.as_of_date == latest_date)
            if sleeve:
                stmt = stmt.where(StrategySnapshot.sleeve == sleeve)
            overlays = list(self.db.scalars(stmt).all())

            # Key by (symbol, sleeve), not (symbol, market), because PositionValuation
            # in your current app does not expose .market.
            overlay_map = {(row.symbol, row.sleeve): row for row in overlays}

        rows: list[OverlayRow] = []

        for p in positions:
            position_symbol = getattr(p, "symbol")
            position_sleeve = getattr(p, "sleeve")

            if sleeve and position_sleeve != sleeve:
                continue

            overlay = overlay_map.get((position_symbol, position_sleeve))

            current_mv = getattr(p, "market_value_base", None) or Decimal("0")
            weight = Decimal("0") if total_nav == 0 else current_mv / total_nav

            rows.append(
                OverlayRow(
                    symbol=position_symbol,
                    security_name=getattr(p, "security_name", position_symbol),
                    sleeve=position_sleeve,
                    market=self._infer_market(position_sleeve, overlay),
                    country=getattr(
                        p,
                        "country",
                        self._infer_country(position_sleeve, overlay),
                    ),
                    current_market_value_base=current_mv,
                    current_weight_of_nav=weight,
                    strategy_state=overlay.strategy_state if overlay else None,
                    target_state=overlay.target_state if overlay else None,
                    target_weight=overlay.target_weight if overlay else None,
                    target_dollars=overlay.target_dollars if overlay else None,
                    actual_position_dollars=overlay.actual_position_dollars if overlay else current_mv,
                    actual_vs_target_delta=overlay.actual_vs_target_delta if overlay else None,
                    eligibility_status=overlay.eligibility_status if overlay else None,
                    buy_list_status=overlay.buy_list_status if overlay else None,
                    reason_code=overlay.reason_code if overlay else None,
                    as_of_date=overlay.as_of_date if overlay else latest_date,
                )
            )

        return rows

    def get_recent_decision_logs(
        self,
        limit: int = 50,
        sleeve: str | None = None,
    ) -> list[DailyDecisionLog]:
        stmt = select(DailyDecisionLog).order_by(
            DailyDecisionLog.decision_date.desc(),
            DailyDecisionLog.id.desc(),
        )
        if sleeve:
            stmt = stmt.where(DailyDecisionLog.sleeve == sleeve)
        stmt = stmt.limit(limit)
        return list(self.db.scalars(stmt).all())