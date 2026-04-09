from pprint import pprint

from backend.app.db.session import SessionLocal
from backend.app.services.sync.full_sync_service import FullSyncService


def main() -> None:
    db = SessionLocal()
    try:
        service = FullSyncService(db)
        result = service.run()

        print("Full sync complete.")
        pprint(
            {
                "started_at": result.started_at.isoformat(),
                "finished_at": result.finished_at.isoformat(),
                "fx_sync_run_id": result.fx_sync_run_id,
                "kiwoom_sync_run_id": result.kiwoom_sync_run_id,
                "fx_rates_written": result.fx_rates_written,
                "holdings_written": result.holdings_written,
                "cash_rows_written": result.cash_rows_written,
                "prices_written": result.prices_written,
                "carry_forward_holdings": result.carry_forward_holdings,
                "carry_forward_cash": result.carry_forward_cash,
                "warning_count": result.warning_count,
                "error_count": result.error_count,
                "snapshot_time": result.snapshot_time.isoformat(),
            }
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()