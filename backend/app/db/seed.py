from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from backend.app.db.session import SessionLocal
from backend.app.db.models import (
    Account,
    CashBalanceSnapshot,
    DataIssue,
    FxRateSnapshot,
    HoldingSnapshot,
    PriceSnapshot,
    SectorMapping,
    SyncRun,
)

from backend.app.core.config import settings

def d(value: str) -> Decimal:
    return Decimal(value)


def reset_tables(db) -> None:
    # Delete child / snapshot tables first
    db.query(HoldingSnapshot).delete()
    db.query(CashBalanceSnapshot).delete()
    db.query(PriceSnapshot).delete()
    db.query(FxRateSnapshot).delete()
    db.query(SectorMapping).delete()
    db.query(DataIssue).delete()
    db.query(SyncRun).delete()
    db.query(Account).delete()
    db.commit()

def ensure_seed_allowed() -> None:
    if settings.app_env.lower() != "development":
        raise RuntimeError("Seeding is only allowed when APP_ENV=development.")

    if not settings.enable_dev_seed_commands:
        raise RuntimeError(
            "Seed command is disabled. Set ENABLE_DEV_SEED_COMMANDS=true to run dev seed."
        )

def seed() -> None:
    ensure_seed_allowed()
    db = SessionLocal()
    try:
        reset_tables(db)

        snapshot_time = datetime.now(UTC)

        # Base currency is USD.
        # Example FX assumption:
        # 1 USD = 1370 KRW
        # Therefore 1 KRW = 0.000729927 USD
        krw_to_usd = d("0.000729927")
        usd_to_usd = d("1.0")

        account = Account(
            broker_name="Kiwoom",
            account_label="Primary",
            market_scope="BOTH",
            base_currency="USD",
            is_active=True,
        )
        db.add(account)
        db.flush()  # get account.id

        # FX snapshots
        db.add_all(
            [
                FxRateSnapshot(
                    base_currency="KRW",
                    quote_currency="USD",
                    rate=krw_to_usd,
                    rate_timestamp=snapshot_time,
                    source_type="seed",
                ),
                FxRateSnapshot(
                    base_currency="USD",
                    quote_currency="USD",
                    rate=usd_to_usd,
                    rate_timestamp=snapshot_time,
                    source_type="seed",
                ),
            ]
        )

        # Sector mappings
        db.add_all(
            [
                SectorMapping(
                    symbol="005930",
                    market="KRX",
                    sector="Information Technology",
                    industry="Semiconductors",
                    updated_at=snapshot_time,
                ),
                SectorMapping(
                    symbol="000660",
                    market="KRX",
                    sector="Information Technology",
                    industry="Semiconductors",
                    updated_at=snapshot_time,
                ),
                SectorMapping(
                    symbol="AAPL",
                    market="NASDAQ",
                    sector="Information Technology",
                    industry="Consumer Electronics",
                    updated_at=snapshot_time,
                ),
                SectorMapping(
                    symbol="MSFT",
                    market="NASDAQ",
                    sector="Information Technology",
                    industry="Software",
                    updated_at=snapshot_time,
                ),
            ]
        )

        # Price snapshots
        db.add_all(
            [
                PriceSnapshot(
                    symbol="005930",
                    market="KRX",
                    currency="KRW",
                    price=d("85000"),
                    price_timestamp=snapshot_time,
                    source_type="seed",
                ),
                PriceSnapshot(
                    symbol="000660",
                    market="KRX",
                    currency="KRW",
                    price=d("205000"),
                    price_timestamp=snapshot_time,
                    source_type="seed",
                ),
                PriceSnapshot(
                    symbol="AAPL",
                    market="NASDAQ",
                    currency="USD",
                    price=d("215"),
                    price_timestamp=snapshot_time,
                    source_type="seed",
                ),
                PriceSnapshot(
                    symbol="MSFT",
                    market="NASDAQ",
                    currency="USD",
                    price=d("425"),
                    price_timestamp=snapshot_time,
                    source_type="seed",
                ),
            ]
        )

        # Cash balances
        krw_cash_native = d("12000000")
        usd_cash_native = d("15000")

        db.add_all(
            [
                CashBalanceSnapshot(
                    account_id=account.id,
                    snapshot_time=snapshot_time,
                    currency="KRW",
                    amount_native=krw_cash_native,
                    fx_rate_to_base=krw_to_usd,
                    amount_base=(krw_cash_native * krw_to_usd).quantize(d("0.0001")),
                    source_type="seed",
                    source_run_id=None,
                ),
                CashBalanceSnapshot(
                    account_id=account.id,
                    snapshot_time=snapshot_time,
                    currency="USD",
                    amount_native=usd_cash_native,
                    fx_rate_to_base=usd_to_usd,
                    amount_base=usd_cash_native,
                    source_type="seed",
                    source_run_id=None,
                ),
            ]
        )

        # Holdings: Korea
        samsung_qty = d("120")
        samsung_avg_cost = d("78000")
        samsung_price = d("85000")
        samsung_cost_basis = samsung_qty * samsung_avg_cost
        samsung_market_value = samsung_qty * samsung_price

        hynix_qty = d("35")
        hynix_avg_cost = d("182000")
        hynix_price = d("205000")
        hynix_cost_basis = hynix_qty * hynix_avg_cost
        hynix_market_value = hynix_qty * hynix_price

        # Holdings: US
        aapl_qty = d("45")
        aapl_avg_cost = d("190")
        aapl_price = d("215")
        aapl_cost_basis = aapl_qty * aapl_avg_cost
        aapl_market_value = aapl_qty * aapl_price

        msft_qty = d("20")
        msft_avg_cost = d("380")
        msft_price = d("425")
        msft_cost_basis = msft_qty * msft_avg_cost
        msft_market_value = msft_qty * msft_price

        holdings = [
            HoldingSnapshot(
                account_id=account.id,
                snapshot_time=snapshot_time,
                symbol="005930",
                security_name="Samsung Electronics",
                market="KRX",
                country="KR",
                sleeve="KR",
                sector="Information Technology",
                industry="Semiconductors",
                currency="KRW",
                quantity=samsung_qty,
                avg_cost_native=samsung_avg_cost,
                current_price_native=samsung_price,
                cost_basis_native=samsung_cost_basis,
                market_value_native=samsung_market_value,
                unrealized_pnl_native=samsung_market_value - samsung_cost_basis,
                unrealized_return_pct=((samsung_market_value - samsung_cost_basis) / samsung_cost_basis),
                fx_rate_to_base=krw_to_usd,
                cost_basis_base=(samsung_cost_basis * krw_to_usd).quantize(d("0.0001")),
                market_value_base=(samsung_market_value * krw_to_usd).quantize(d("0.0001")),
                unrealized_pnl_base=((samsung_market_value - samsung_cost_basis) * krw_to_usd).quantize(d("0.0001")),
                price_timestamp=snapshot_time,
                source_type="seed",
                source_run_id=None,
            ),
            HoldingSnapshot(
                account_id=account.id,
                snapshot_time=snapshot_time,
                symbol="000660",
                security_name="SK Hynix",
                market="KRX",
                country="KR",
                sleeve="KR",
                sector="Information Technology",
                industry="Semiconductors",
                currency="KRW",
                quantity=hynix_qty,
                avg_cost_native=hynix_avg_cost,
                current_price_native=hynix_price,
                cost_basis_native=hynix_cost_basis,
                market_value_native=hynix_market_value,
                unrealized_pnl_native=hynix_market_value - hynix_cost_basis,
                unrealized_return_pct=((hynix_market_value - hynix_cost_basis) / hynix_cost_basis),
                fx_rate_to_base=krw_to_usd,
                cost_basis_base=(hynix_cost_basis * krw_to_usd).quantize(d("0.0001")),
                market_value_base=(hynix_market_value * krw_to_usd).quantize(d("0.0001")),
                unrealized_pnl_base=((hynix_market_value - hynix_cost_basis) * krw_to_usd).quantize(d("0.0001")),
                price_timestamp=snapshot_time,
                source_type="seed",
                source_run_id=None,
            ),
            HoldingSnapshot(
                account_id=account.id,
                snapshot_time=snapshot_time,
                symbol="AAPL",
                security_name="Apple Inc.",
                market="NASDAQ",
                country="US",
                sleeve="US",
                sector="Information Technology",
                industry="Consumer Electronics",
                currency="USD",
                quantity=aapl_qty,
                avg_cost_native=aapl_avg_cost,
                current_price_native=aapl_price,
                cost_basis_native=aapl_cost_basis,
                market_value_native=aapl_market_value,
                unrealized_pnl_native=aapl_market_value - aapl_cost_basis,
                unrealized_return_pct=((aapl_market_value - aapl_cost_basis) / aapl_cost_basis),
                fx_rate_to_base=usd_to_usd,
                cost_basis_base=aapl_cost_basis,
                market_value_base=aapl_market_value,
                unrealized_pnl_base=aapl_market_value - aapl_cost_basis,
                price_timestamp=snapshot_time,
                source_type="seed",
                source_run_id=None,
            ),
            HoldingSnapshot(
                account_id=account.id,
                snapshot_time=snapshot_time,
                symbol="MSFT",
                security_name="Microsoft Corp.",
                market="NASDAQ",
                country="US",
                sleeve="US",
                sector="Information Technology",
                industry="Software",
                currency="USD",
                quantity=msft_qty,
                avg_cost_native=msft_avg_cost,
                current_price_native=msft_price,
                cost_basis_native=msft_cost_basis,
                market_value_native=msft_market_value,
                unrealized_pnl_native=msft_market_value - msft_cost_basis,
                unrealized_return_pct=((msft_market_value - msft_cost_basis) / msft_cost_basis),
                fx_rate_to_base=usd_to_usd,
                cost_basis_base=msft_cost_basis,
                market_value_base=msft_market_value,
                unrealized_pnl_base=msft_market_value - msft_cost_basis,
                price_timestamp=snapshot_time,
                source_type="seed",
                source_run_id=None,
            ),
        ]

        db.add_all(holdings)
        db.commit()

        print("Seed complete.")
        print(f"Account ID: {account.id}")
        print(f"Snapshot time: {snapshot_time.isoformat()}")
        print("Inserted:")
        print("- 1 account")
        print("- 2 cash balance snapshots")
        print("- 4 price snapshots")
        print("- 2 fx rate snapshots")
        print("- 4 sector mappings")
        print("- 4 holding snapshots")

    finally:
        db.close()


if __name__ == "__main__":
    seed()