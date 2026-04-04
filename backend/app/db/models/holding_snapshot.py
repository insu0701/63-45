from datetime import datetime, UTC

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class HoldingSnapshot(Base):
    __tablename__ = "holding_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False, index=True)
    snapshot_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    symbol: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    security_name: Mapped[str] = mapped_column(String(200), nullable=False)
    market: Mapped[str] = mapped_column(String(50), nullable=False)   # KRX, NASDAQ, NYSE
    country: Mapped[str] = mapped_column(String(10), nullable=False)  # KR, US
    sleeve: Mapped[str] = mapped_column(String(10), nullable=False)   # KR, US
    sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)

    quantity: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    avg_cost_native: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    current_price_native: Mapped[float | None] = mapped_column(Numeric(20, 6), nullable=True)
    cost_basis_native: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    market_value_native: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    unrealized_pnl_native: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    unrealized_return_pct: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)

    fx_rate_to_base: Mapped[float | None] = mapped_column(Numeric(20, 8), nullable=True)
    cost_basis_base: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    market_value_base: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)
    unrealized_pnl_base: Mapped[float | None] = mapped_column(Numeric(20, 4), nullable=True)

    price_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))