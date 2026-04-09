from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.services.sync.fx_sync_service import FxSyncService
from backend.app.services.sync.kiwoom_sync_service import KiwoomSyncService
from backend.app.services.sync.price_sync_service import PriceSyncService


@dataclass
class FullSyncResult:
    started_at: datetime
    finished_at: datetime
    fx_sync_run_id: int
    kiwoom_sync_run_id: int
    price_sync_run_id: int
    fx_rates_written: int
    holdings_written: int
    cash_rows_written: int
    prices_written: int
    carry_forward_holdings: int
    carry_forward_cash: int
    price_refresh_holdings_written: int
    price_refresh_prices_written: int
    price_carry_forward_symbols: int
    warning_count: int
    error_count: int
    snapshot_time: datetime


class FullSyncService:
    def __init__(self, db: Session):
        self.db = db

    def run(self) -> FullSyncResult:
        started_at = datetime.now(UTC)

        fx_result = FxSyncService(self.db).run()
        kiwoom_result = KiwoomSyncService(self.db).run()
        price_result = PriceSyncService(self.db).run()

        finished_at = datetime.now(UTC)

        return FullSyncResult(
            started_at=started_at,
            finished_at=finished_at,
            fx_sync_run_id=fx_result.sync_run_id,
            kiwoom_sync_run_id=kiwoom_result.sync_run_id,
            price_sync_run_id=price_result.sync_run_id,
            fx_rates_written=fx_result.rates_written,
            holdings_written=kiwoom_result.holdings_written,
            cash_rows_written=kiwoom_result.cash_rows_written,
            prices_written=kiwoom_result.prices_written,
            carry_forward_holdings=kiwoom_result.carry_forward_holdings,
            carry_forward_cash=kiwoom_result.carry_forward_cash,
            price_refresh_holdings_written=price_result.holdings_written,
            price_refresh_prices_written=price_result.prices_written,
            price_carry_forward_symbols=price_result.carry_forward_symbols,
            warning_count=(
                fx_result.warning_count
                + kiwoom_result.warning_count
                + price_result.warning_count
            ),
            error_count=(
                fx_result.error_count
                + kiwoom_result.error_count
                + price_result.error_count
            ),
            snapshot_time=price_result.snapshot_time,
        )