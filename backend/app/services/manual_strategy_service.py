from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.strategy_options import (
    ALLOWED_BUY_LIST_STATUSES,
    ALLOWED_ELIGIBILITY_STATUSES,
    ALLOWED_REASON_CODES,
    ALLOWED_STRATEGY_STATES,
    ALLOWED_TARGET_STATES,
)
from backend.app.db.models import DailyDecisionLog, HoldingSnapshot, StrategySnapshot
from backend.app.services.active_snapshot_service import ActiveSnapshotService


@dataclass
class ManualStrategyOverlayResult:
    overlay_id: int
    symbol: str
    sleeve: str
    as_of_date: date
    reason_code: str
    actual_position_dollars: Decimal
    target_dollars: Decimal | None
    actual_vs_target_delta: Decimal | None
    decision_log_written: bool


class ManualStrategyService:
    def __init__(self, db: Session):
        self.db = db
        self.active_snapshot_service = ActiveSnapshotService(db)

    def _validate_optional_choice(
        self,
        *,
        field_name: str,
        value: str | None,
        allowed_values: set[str],
    ) -> None:
        if value is None:
            return
        if value not in allowed_values:
            raise ValueError(f"Invalid {field_name}: {value}")

    def _to_decimal(self, value: Any) -> Decimal | None:
        if value is None:
            return None
        return Decimal(str(value))

    def _get_latest_holding(self, symbol: str, sleeve: str) -> HoldingSnapshot:
        latest_ts = self.active_snapshot_service.get_active_holdings_snapshot_time()
        if latest_ts is None:
            raise RuntimeError("No active holdings snapshot found.")

        stmt = (
            select(HoldingSnapshot)
            .where(HoldingSnapshot.snapshot_time == latest_ts)
            .where(HoldingSnapshot.symbol == symbol)
            .where(HoldingSnapshot.sleeve == sleeve)
            .limit(1)
        )
        row = self.db.scalar(stmt)

        if row is None:
            raise RuntimeError(f"No active holding found for symbol={symbol}, sleeve={sleeve}.")

        return row

    def upsert_overlay(
        self,
        *,
        symbol: str,
        sleeve: str,
        strategy_state: str | None,
        target_state: str | None,
        target_weight: float | None,
        target_dollars: float | None,
        eligibility_status: str | None,
        buy_list_status: str | None,
        reason_code: str,
        notes: str | None,
        append_decision_log: bool,
    ) -> ManualStrategyOverlayResult:
        self._validate_optional_choice(
            field_name="strategy_state",
            value=strategy_state,
            allowed_values=ALLOWED_STRATEGY_STATES,
        )
        self._validate_optional_choice(
            field_name="target_state",
            value=target_state,
            allowed_values=ALLOWED_TARGET_STATES,
        )
        self._validate_optional_choice(
            field_name="eligibility_status",
            value=eligibility_status,
            allowed_values=ALLOWED_ELIGIBILITY_STATUSES,
        )
        self._validate_optional_choice(
            field_name="buy_list_status",
            value=buy_list_status,
            allowed_values=ALLOWED_BUY_LIST_STATUSES,
        )

        if reason_code not in ALLOWED_REASON_CODES:
            raise ValueError(f"Invalid reason_code: {reason_code}")

        holding = self._get_latest_holding(symbol=symbol, sleeve=sleeve)

        today = date.today()
        now = datetime.now(UTC)

        existing_stmt = (
            select(StrategySnapshot)
            .where(StrategySnapshot.as_of_date == today)
            .where(StrategySnapshot.symbol == symbol)
            .where(StrategySnapshot.sleeve == sleeve)
            .order_by(StrategySnapshot.created_at.desc())
            .limit(1)
        )
        overlay = self.db.scalar(existing_stmt)

        actual_position_dollars = self._to_decimal(holding.market_value_base) or Decimal("0")
        target_dollars_decimal = self._to_decimal(target_dollars)
        target_weight_decimal = self._to_decimal(target_weight)
        actual_vs_target_delta = (
            actual_position_dollars - target_dollars_decimal
            if target_dollars_decimal is not None
            else None
        )

        if overlay is None:
            overlay = StrategySnapshot(
                as_of_date=today,
                account_id=holding.account_id,
                symbol=holding.symbol,
                market=holding.market,
                country=holding.country,
                sleeve=holding.sleeve,
                created_at=now,
            )
            self.db.add(overlay)

        overlay.account_id = holding.account_id
        overlay.symbol = holding.symbol
        overlay.market = holding.market
        overlay.country = holding.country
        overlay.sleeve = holding.sleeve
        overlay.strategy_state = strategy_state
        overlay.target_state = target_state
        overlay.target_weight = target_weight_decimal
        overlay.target_dollars = target_dollars_decimal
        overlay.actual_position_dollars = actual_position_dollars
        overlay.actual_vs_target_delta = actual_vs_target_delta
        overlay.eligibility_status = eligibility_status
        overlay.buy_list_status = buy_list_status
        overlay.reason_code = reason_code
        overlay.source_type = "manual_input"
        overlay.source_run_id = None
        overlay.notes = notes

        decision_log_written = False

        if append_decision_log:
            decision_log = DailyDecisionLog(
                decision_date=today,
                decision_timestamp=now,
                account_id=holding.account_id,
                symbol=holding.symbol,
                market=holding.market,
                sleeve=holding.sleeve,
                sector=holding.sector,
                eligibility_status=eligibility_status,
                buy_list_status=buy_list_status,
                morningstar_status=None,
                foreign_buy_list_status=None,
                foreign_sell_list_status=None,
                decision_price=holding.current_price_native,
                macd_value=None,
                macd_signal_value=None,
                rsi_value=None,
                rsi_signal_line=None,
                sma20=None,
                ema50=None,
                volatility_estimate=None,
                current_state=strategy_state,
                target_state=target_state,
                current_position_dollars=actual_position_dollars,
                target_position_dollars=target_dollars_decimal,
                generated_order_quantity=None,
                fill_quantity=None,
                rejection_status=None,
                reason_code=reason_code,
                source_type="manual_input",
                source_run_id=None,
                notes=notes,
                created_at=now,
            )
            self.db.add(decision_log)
            decision_log_written = True

        self.db.commit()
        self.db.refresh(overlay)

        return ManualStrategyOverlayResult(
            overlay_id=overlay.id,
            symbol=overlay.symbol,
            sleeve=overlay.sleeve,
            as_of_date=overlay.as_of_date,
            reason_code=overlay.reason_code or reason_code,
            actual_position_dollars=actual_position_dollars,
            target_dollars=target_dollars_decimal,
            actual_vs_target_delta=actual_vs_target_delta,
            decision_log_written=decision_log_written,
        )