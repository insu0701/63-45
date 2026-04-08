from pprint import pprint

from backend.app.db.session import SessionLocal
from backend.app.services.sync.kiwoom_sync_service import KiwoomSyncService


def main() -> None:
    db = SessionLocal()
    try:
        service = KiwoomSyncService(db)
        result = service.run()

        print("Kiwoom sync complete.")
        pprint(
            {
                "sync_run_id": result.sync_run_id,
                "snapshot_time": result.snapshot_time.isoformat(),
                "holdings_written": result.holdings_written,
                "cash_rows_written": result.cash_rows_written,
                "prices_written": result.prices_written,
                "carry_forward_holdings": result.carry_forward_holdings,
                "carry_forward_cash": result.carry_forward_cash,
                "warning_count": result.warning_count,
                "error_count": result.error_count,
                "archive_paths": result.archive_paths,
            }
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()