from pprint import pprint

from backend.app.db.session import SessionLocal
from backend.app.services.sync.price_sync_service import PriceSyncService


def main() -> None:
    db = SessionLocal()
    try:
        service = PriceSyncService(db)
        result = service.run()

        print("Price sync complete.")
        pprint(
            {
                "sync_run_id": result.sync_run_id,
                "snapshot_time": result.snapshot_time.isoformat(),
                "holdings_written": result.holdings_written,
                "prices_written": result.prices_written,
                "kr_symbols_priced": result.kr_symbols_priced,
                "us_symbols_priced": result.us_symbols_priced,
                "carry_forward_symbols": result.carry_forward_symbols,
                "warning_count": result.warning_count,
                "error_count": result.error_count,
            }
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()