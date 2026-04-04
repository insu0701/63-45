from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class CashBalanceSnapshot(Base):
    __tablename__ = "cash_balance_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)
    snapshot_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    amount_native: Mapped[float] = mapped_column(Numeric(20, 4), nullable=False)
    fx_rate_to_base: Mapped[float | None] = mapped_column(Numeric(20, 8), nullable=True)
    amount_base: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))