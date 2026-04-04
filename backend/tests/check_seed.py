from sqlalchemy import func, select

from backend.app.db.models import (
    Account,
    CashBalanceSnapshot,
    HoldingSnapshot,
    FxRateSnapshot,
    PriceSnapshot,
    SectorMapping,
)
from backend.app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()
    try:
        counts = {
            "accounts": db.scalar(select(func.count()).select_from(Account)),
            "cash_balance_snapshots": db.scalar(select(func.count()).select_from(CashBalanceSnapshot)),
            "holding_snapshots": db.scalar(select(func.count()).select_from(HoldingSnapshot)),
            "fx_rate_snapshots": db.scalar(select(func.count()).select_from(FxRateSnapshot)),
            "price_snapshots": db.scalar(select(func.count()).select_from(PriceSnapshot)),
            "sector_mappings": db.scalar(select(func.count()).select_from(SectorMapping)),
        }

        print("Seed row counts:")
        for k, v in counts.items():
            print(f"{k}: {v}")

    finally:
        db.close()


if __name__ == "__main__":
    main()