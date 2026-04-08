from __future__ import annotations

from datetime import date, datetime, UTC
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class StrategySnapshot(Base):
    __tablename__ = "strategy_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    as_of_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=True,
        index=True,
    )

    symbol: Mapped[str] = mapped_column(String, nullable=False, index=True)
    market: Mapped[str] = mapped_column(String, nullable=False, index=True)
    country: Mapped[str] = mapped_column(String, nullable=False)
    sleeve: Mapped[str] = mapped_column(String, nullable=False, index=True)

    strategy_state: Mapped[str | None] = mapped_column(String, nullable=True)
    target_state: Mapped[str | None] = mapped_column(String, nullable=True)

    target_weight: Mapped[Decimal | None] = mapped_column(Numeric(18, 8), nullable=True)
    target_dollars: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)

    actual_position_dollars: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    actual_vs_target_delta: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)

    eligibility_status: Mapped[str | None] = mapped_column(String, nullable=True)
    buy_list_status: Mapped[str | None] = mapped_column(String, nullable=True)
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