from __future__ import annotations

from decimal import Decimal

from backend.app.db.session import SessionLocal
from backend.app.services.manual_strategy_service import ManualStrategyService
from backend.app.services.strategy_overlay_service import StrategyOverlayService


def main() -> None:
    db = SessionLocal()
    try:
        overlay_service = StrategyOverlayService(db)
        manual_service = ManualStrategyService(db)

        rows = overlay_service.get_overlay_rows()
        if not rows:
            raise RuntimeError("No strategy overlay rows available. Seed placeholders first.")

        examples = [
            ("MANUAL_TARGET_SET", "STATE_3", "STATE_3", "eligible", "in_buy_list", None),
            ("MANUAL_WAIT_SIGNAL", "STATE_1", "STATE_2", "eligible", "in_buy_list", Decimal("0.75")),
            ("MANUAL_TRIM", "STATE_3", "STATE_1", "eligible", "held_not_buyable", Decimal("0.40")),
            ("MANUAL_BLOCK_RISK", "STATE_1", "STATE_0", "blocked", "out_of_buy_list", Decimal("0.00")),
        ]

        for row, example in zip(rows[:4], examples, strict=False):
            reason_code, strategy_state, target_state, eligibility_status, buy_list_status, multiple = example

            target_dollars = None
            if multiple is None:
                target_dollars = row.current_market_value_base
            else:
                target_dollars = row.current_market_value_base * multiple

            manual_service.upsert_overlay(
                symbol=row.symbol,
                sleeve=row.sleeve,
                strategy_state=strategy_state,
                target_state=target_state,
                target_weight=None,
                target_dollars=target_dollars,
                eligibility_status=eligibility_status,
                buy_list_status=buy_list_status,
                reason_code=reason_code,
                notes="Seeded Step 15 manual strategy example.",
                append_decision_log=True,
            )

        print("Manual strategy examples seeded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()