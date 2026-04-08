import argparse
from pathlib import Path
from pprint import pprint
from decimal import Decimal

from backend.app.db.session import SessionLocal
from backend.app.services.imports.us_holdings_csv_import_service import UsHoldingsCsvImportService


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", type=str)
    parser.add_argument("--usd-cash", type=str, required=True)
    args = parser.parse_args()

    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    file_bytes = csv_path.read_bytes()
    usd_cash = Decimal(args.usd_cash)

    db = SessionLocal()
    try:
        service = UsHoldingsCsvImportService(db)
        result = service.run(file_bytes=file_bytes, usd_cash=usd_cash)

        print("US CSV import complete.")
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
                "imported_symbols": result.imported_symbols,
            }
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()