from __future__ import annotations

from datetime import date, datetime, UTC
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class DailyDecisionLog(Base):
    __tablename__ = "daily_decision_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    decision_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    decision_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=True,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    market: Mapped[str] = mapped_column(String, nullable=False, index=True)
    sleeve: Mapped[str] = mapped_column(String, nullable=False, index=True)
    sector: Mapped[str | None] = mapped_column(String, nullable=True)

    eligibility_status: Mapped[str | None] = mapped_column(String, nullable=True)
    buy_list_status: Mapped[str | None] = mapped_column(String, nullable=True)
    morningstar_status: Mapped[str | None] = mapped_column(String, nullable=True)
    foreign_buy_list_status: Mapped[str | None] = mapped_column(String, nullable=True)
    foreign_sell_list_status: Mapped[str | None] = mapped_column(String, nullable=True)

    decision_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)

    macd_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    macd_signal_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    rsi_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    rsi_signal_line: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    sma20: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    ema50: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    volatility_estimate: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)

    current_state: Mapped[str | None] = mapped_column(String, nullable=True)
    target_state: Mapped[str | None] = mapped_column(String, nullable=True)

    current_position_dollars: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    target_position_dollars: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)

    generated_order_quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    fill_quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    rejection_status: Mapped[str | None] = mapped_column(String, nullable=True)

    reason_code: Mapped[str | None] = mapped_column(String, nullable=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False, default="manual_stub")
    source_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("sync_runs.id"),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )