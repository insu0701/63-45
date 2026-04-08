from __future__ import annotations

import argparse

from sqlalchemy import delete

from backend.app.core.config import settings
from backend.app.db.models import (
    CashBalanceSnapshot,
    DataIssue,
    HoldingSnapshot,
    PriceSnapshot,
    SyncRun,
)
from backend.app.db.seed import seed
from backend.app.db.session import SessionLocal


def ensure_reset_allowed() -> None:
    if settings.app_env.lower() != "development":
        raise RuntimeError("Dev reset is only allowed when APP_ENV=development.")

    if not settings.enable_dev_reset_commands:
        raise RuntimeError(
            "Dev reset command is disabled. Set ENABLE_DEV_RESET_COMMANDS=true to use it."
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--with-seed",
        action="store_true",
        help="After reset, run dev seed data.",
    )
    args = parser.parse_args()

    ensure_reset_allowed()

    db = SessionLocal()
    try:
        db.execute(delete(HoldingSnapshot))
        db.execute(delete(CashBalanceSnapshot))
        db.execute(delete(PriceSnapshot))
        db.execute(delete(DataIssue))
        db.execute(delete(SyncRun))
        db.commit()

        print("Dev data reset complete.")
        print("Deleted:")
        print("- holding_snapshots")
        print("- cash_balance_snapshots")
        print("- price_snapshots")
        print("- data_issues")
        print("- sync_runs")
    finally:
        db.close()

    if args.with_seed:
        seed()
        print("Dev seed completed after reset.")


if __name__ == "__main__":
    main()