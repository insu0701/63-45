from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.models import CashBalanceSnapshot, HoldingSnapshot, PriceSnapshot


class ActiveSnapshotService:
    def __init__(self, db: Session):
        self.db = db

    def _latest_snapshot_time(self, model, ts_column, source_column):
        stmt = (
            select(ts_column)
            .where(source_column != "seed")
            .order_by(ts_column.desc())
            .limit(1)
        )
        ts = self.db.scalar(stmt)

        if ts is not None:
            return ts

        if settings.allow_seed_fallback:
            return self.db.scalar(
                select(ts_column)
                .order_by(ts_column.desc())
                .limit(1)
            )

        return None

    def get_active_holdings_snapshot_time(self):
        return self._latest_snapshot_time(
            HoldingSnapshot,
            HoldingSnapshot.snapshot_time,
            HoldingSnapshot.source_type,
        )

    def get_active_cash_snapshot_time(self):
        return self._latest_snapshot_time(
            CashBalanceSnapshot,
            CashBalanceSnapshot.snapshot_time,
            CashBalanceSnapshot.source_type,
        )

    def get_active_price_snapshot_time(self):
        return self._latest_snapshot_time(
            PriceSnapshot,
            PriceSnapshot.price_timestamp,
            PriceSnapshot.source_type,
        )