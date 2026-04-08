from pprint import pprint

from backend.app.db.session import SessionLocal
from backend.app.services.sync.fx_sync_service import FxSyncService


def main() -> None:
    db = SessionLocal()
    try:
        service = FxSyncService(db)
        result = service.run()

        print("FX sync complete.")
        pprint(
            {
                "sync_run_id": result.sync_run_id,
                "snapshot_time": result.snapshot_time.isoformat(),
                "rates_written": result.rates_written,
                "warning_count": result.warning_count,
                "error_count": result.error_count,
                "provider": result.provider,
            }
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()