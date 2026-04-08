from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import delete, func, select

from backend.app.db.models import DailyDecisionLog, HoldingSnapshot, StrategySnapshot
from backend.app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()

    try:
        latest_snapshot_time = db.scalar(
            select(func.max(HoldingSnapshot.snapshot_time))
        )

        if latest_snapshot_time is None:
            raise RuntimeError(
                "No holding snapshots found. Run Kiwoom sync / US import before seeding strategy placeholders."
            )

        holdings = list(
            db.scalars(
                select(HoldingSnapshot)
                .where(HoldingSnapshot.snapshot_time == latest_snapshot_time)
                .order_by(HoldingSnapshot.market_value_base.desc())
            ).all()
        )

        if not holdings:
            raise RuntimeError(
                "Latest holding snapshot contains no rows. Cannot seed strategy placeholders."
            )

        today = date.today()

        db.execute(
            delete(StrategySnapshot).where(
                StrategySnapshot.as_of_date == today,
                StrategySnapshot.source_type == "manual_stub",
            )
        )

        db.execute(
            delete(DailyDecisionLog).where(
                DailyDecisionLog.decision_date == today,
                DailyDecisionLog.source_type == "manual_stub",
            )
        )

        for holding in holdings:
            strategy_row = StrategySnapshot(
                as_of_date=today,
                account_id=holding.account_id,
                symbol=holding.symbol,
                market=holding.market,
                country=holding.country,
                sleeve=holding.sleeve,
                strategy_state="STATE_0",
                target_state=None,
                target_weight=None,
                target_dollars=None,
                actual_position_dollars=holding.market_value_base,
                actual_vs_target_delta=None,
                eligibility_status="unknown",
                buy_list_status="unknown",
                reason_code="MANUAL_PLACEHOLDER",
                source_type="manual_stub",
                source_run_id=None,
                notes="Placeholder strategy overlay row created for Step 14.",
                created_at=datetime.now(UTC),
            )
            db.add(strategy_row)

        top_holdings = holdings[: min(5, len(holdings))]

        for holding in top_holdings:
            decision_row = DailyDecisionLog(
                decision_date=today,
                decision_timestamp=datetime.now(UTC),
                account_id=holding.account_id,
                symbol=holding.symbol,
                market=holding.market,
                sleeve=holding.sleeve,
                sector=holding.sector,
                eligibility_status="unknown",
                buy_list_status="unknown",
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
                current_state="STATE_0",
                target_state=None,
                current_position_dollars=holding.market_value_base,
                target_position_dollars=None,
                generated_order_quantity=None,
                fill_quantity=None,
                rejection_status=None,
                reason_code="MANUAL_PLACEHOLDER",
                source_type="manual_stub",
                source_run_id=None,
                notes="Placeholder daily decision log row created for Step 14.",
                created_at=datetime.now(UTC),
            )
            db.add(decision_row)

        db.commit()

        print("Strategy placeholder seed complete.")
        print(f"Latest holding snapshot time: {latest_snapshot_time.isoformat()}")
        print(f"Strategy rows inserted: {len(holdings)}")
        print(f"Decision log rows inserted: {len(top_holdings)}")

    finally:
        db.close()


if __name__ == "__main__":
    main()