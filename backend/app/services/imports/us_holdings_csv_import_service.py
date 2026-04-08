from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.models import (
    Account,
    CashBalanceSnapshot,
    DataIssue,
    HoldingSnapshot,
    PriceSnapshot,
    SyncRun,
)


def parse_decimal(value: Any) -> Decimal:
    text = str(value).strip()
    if text == "":
        raise ValueError("Empty numeric value.")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid decimal value: {value}") from exc


@dataclass
class UsCsvImportResult:
    sync_run_id: int
    snapshot_time: datetime
    holdings_written: int
    cash_rows_written: int
    prices_written: int
    carry_forward_holdings: int
    carry_forward_cash: int
    warning_count: int
    error_count: int
    imported_symbols: list[str]


class UsHoldingsCsvImportService:
    REQUIRED_COLUMNS = {
        "symbol",
        "security_name",
        "quantity",
        "avg_cost_usd",
        "current_price_usd",
    }

    def __init__(self, db: Session):
        self.db = db
        self._warning_count = 0
        self._error_count = 0

    def _create_sync_run(self) -> SyncRun:
        sync_run = SyncRun(
            source_type="manual_import",
            job_name="us_holdings_csv_import",
            started_at=datetime.now(UTC),
            finished_at=None,
            status="running",
            records_processed=0,
            warning_count=0,
            error_count=0,
            message=None,
        )
        self.db.add(sync_run)
        self.db.commit()
        self.db.refresh(sync_run)
        return sync_run

    def _finalize_sync_run(
        self,
        sync_run: SyncRun,
        *,
        status: str,
        records_processed: int,
        message: str | None = None,
    ) -> None:
        sync_run.finished_at = datetime.now(UTC)
        sync_run.status = status
        sync_run.records_processed = records_processed
        sync_run.warning_count = self._warning_count
        sync_run.error_count = self._error_count
        sync_run.message = message
        self.db.add(sync_run)
        self.db.commit()

    def _create_issue(
        self,
        *,
        sync_run_id: int,
        issue_type: str,
        severity: str,
        description: str,
        symbol: str | None = None,
        market: str | None = None,
    ) -> None:
        issue = DataIssue(
            detected_at=datetime.now(UTC),
            issue_type=issue_type,
            severity=severity,
            symbol=symbol,
            market=market,
            description=description,
            is_resolved=False,
            resolved_at=None,
            source_run_id=sync_run_id,
        )
        self.db.add(issue)

        if severity == "warning":
            self._warning_count += 1
        elif severity == "error":
            self._error_count += 1

    def _get_or_create_manual_us_account(self) -> Account:
        stmt = (
            select(Account)
            .where(Account.broker_name == "ManualImport")
            .where(Account.account_label == "US Manual Import")
            .limit(1)
        )
        account = self.db.scalar(stmt)

        if account is not None:
            return account

        account = Account(
            broker_name="ManualImport",
            account_label="US Manual Import",
            market_scope="US",
            base_currency=settings.base_currency,
            is_active=True,
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def _latest_holdings_snapshot_time(self) -> datetime | None:
        stmt = select(HoldingSnapshot.snapshot_time).order_by(HoldingSnapshot.snapshot_time.desc()).limit(1)
        return self.db.scalar(stmt)

    def _latest_cash_snapshot_time(self) -> datetime | None:
        stmt = select(CashBalanceSnapshot.snapshot_time).order_by(CashBalanceSnapshot.snapshot_time.desc()).limit(1)
        return self.db.scalar(stmt)

    def _carry_forward_non_us_holdings(self, snapshot_time: datetime, sync_run_id: int) -> int:
        latest_ts = self._latest_holdings_snapshot_time()
        if latest_ts is None:
            return 0

        rows = self.db.scalars(
            select(HoldingSnapshot)
            .where(HoldingSnapshot.snapshot_time == latest_ts)
            .where(HoldingSnapshot.sleeve != "US")
        ).all()

        written = 0
        for row in rows:
            clone = HoldingSnapshot(
                account_id=row.account_id,
                snapshot_time=snapshot_time,
                symbol=row.symbol,
                security_name=row.security_name,
                market=row.market,
                country=row.country,
                sleeve=row.sleeve,
                sector=row.sector,
                industry=row.industry,
                currency=row.currency,
                quantity=row.quantity,
                avg_cost_native=row.avg_cost_native,
                current_price_native=row.current_price_native,
                cost_basis_native=row.cost_basis_native,
                market_value_native=row.market_value_native,
                unrealized_pnl_native=row.unrealized_pnl_native,
                unrealized_return_pct=row.unrealized_return_pct,
                fx_rate_to_base=row.fx_rate_to_base,
                cost_basis_base=row.cost_basis_base,
                market_value_base=row.market_value_base,
                unrealized_pnl_base=row.unrealized_pnl_base,
                price_timestamp=row.price_timestamp,
                source_type="carry_forward",
                source_run_id=sync_run_id,
            )
            self.db.add(clone)
            written += 1

        return written

    def _carry_forward_non_usd_cash(self, snapshot_time: datetime, sync_run_id: int) -> int:
        latest_ts = self._latest_cash_snapshot_time()
        if latest_ts is None:
            return 0

        rows = self.db.scalars(
            select(CashBalanceSnapshot)
            .where(CashBalanceSnapshot.snapshot_time == latest_ts)
            .where(CashBalanceSnapshot.currency != "USD")
        ).all()

        written = 0
        for row in rows:
            clone = CashBalanceSnapshot(
                account_id=row.account_id,
                snapshot_time=snapshot_time,
                currency=row.currency,
                amount_native=row.amount_native,
                fx_rate_to_base=row.fx_rate_to_base,
                amount_base=row.amount_base,
                source_type="carry_forward",
                source_run_id=sync_run_id,
            )
            self.db.add(clone)
            written += 1

        return written

    def _parse_csv(self, file_bytes: bytes) -> list[dict[str, str]]:
        decoded = file_bytes.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(decoded))

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")

        fieldnames = {name.strip() for name in reader.fieldnames if name}
        missing = self.REQUIRED_COLUMNS - fieldnames
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        rows: list[dict[str, str]] = []
        for row in reader:
            cleaned = {str(k).strip(): str(v).strip() for k, v in row.items() if k is not None}
            if not any(cleaned.values()):
                continue
            rows.append(cleaned)

        if not rows:
            raise ValueError("CSV file contains no holdings rows.")

        return rows

    def run(self, *, file_bytes: bytes, usd_cash: Decimal) -> UsCsvImportResult:
        sync_run = self._create_sync_run()
        records_processed = 0

        try:
            parsed_rows = self._parse_csv(file_bytes)
            account = self._get_or_create_manual_us_account()
            snapshot_time = datetime.now(UTC)

            carry_forward_holdings = self._carry_forward_non_us_holdings(snapshot_time, sync_run.id)
            carry_forward_cash = self._carry_forward_non_usd_cash(snapshot_time, sync_run.id)

            cash_row = CashBalanceSnapshot(
                account_id=account.id,
                snapshot_time=snapshot_time,
                currency="USD",
                amount_native=usd_cash,
                fx_rate_to_base=Decimal("1"),
                amount_base=usd_cash,
                source_type="manual:us_csv",
                source_run_id=sync_run.id,
            )
            self.db.add(cash_row)
            cash_rows_written = 1

            seen_symbols: set[str] = set()
            imported_symbols: list[str] = []
            holdings_written = 0
            prices_written = 0

            for idx, row in enumerate(parsed_rows, start=2):
                symbol = row["symbol"].upper().strip()
                if not symbol:
                    raise ValueError(f"Row {idx}: symbol is empty.")
                if symbol in seen_symbols:
                    raise ValueError(f"Row {idx}: duplicate symbol '{symbol}'.")
                seen_symbols.add(symbol)

                security_name = row["security_name"].strip()
                quantity = parse_decimal(row["quantity"])
                avg_cost = parse_decimal(row["avg_cost_usd"])
                current_price = parse_decimal(row["current_price_usd"])

                if quantity <= 0:
                    self._create_issue(
                        sync_run_id=sync_run.id,
                        issue_type="us_csv_zero_or_negative_quantity",
                        severity="warning",
                        description=f"Skipped row {idx} for symbol {symbol} because quantity <= 0.",
                        symbol=symbol,
                        market="US",
                    )
                    continue

                market = row.get("market", "").strip().upper() or "US"
                sector = row.get("sector", "").strip() or None
                industry = row.get("industry", "").strip() or None

                cost_basis = quantity * avg_cost
                market_value = quantity * current_price
                unrealized_pnl = market_value - cost_basis
                unrealized_return_pct = Decimal("0") if cost_basis == 0 else unrealized_pnl / cost_basis

                holding = HoldingSnapshot(
                    account_id=account.id,
                    snapshot_time=snapshot_time,
                    symbol=symbol,
                    security_name=security_name,
                    market=market,
                    country="US",
                    sleeve="US",
                    sector=sector,
                    industry=industry,
                    currency="USD",
                    quantity=quantity,
                    avg_cost_native=avg_cost,
                    current_price_native=current_price,
                    cost_basis_native=cost_basis,
                    market_value_native=market_value,
                    unrealized_pnl_native=unrealized_pnl,
                    unrealized_return_pct=unrealized_return_pct,
                    fx_rate_to_base=Decimal("1"),
                    cost_basis_base=cost_basis,
                    market_value_base=market_value,
                    unrealized_pnl_base=unrealized_pnl,
                    price_timestamp=snapshot_time,
                    source_type="manual:us_csv",
                    source_run_id=sync_run.id,
                )
                self.db.add(holding)
                holdings_written += 1

                price = PriceSnapshot(
                    symbol=symbol,
                    market=market,
                    currency="USD",
                    price=current_price,
                    price_timestamp=snapshot_time,
                    source_type="manual:us_csv",
                )
                self.db.add(price)
                prices_written += 1

                imported_symbols.append(symbol)

            if holdings_written == 0:
                raise ValueError("CSV import produced zero valid US holdings rows.")

            self.db.commit()

            records_processed = (
                carry_forward_holdings
                + carry_forward_cash
                + cash_rows_written
                + holdings_written
                + prices_written
            )

            self._finalize_sync_run(
                sync_run,
                status="success",
                records_processed=records_processed,
                message="US holdings CSV import completed successfully.",
            )

            return UsCsvImportResult(
                sync_run_id=sync_run.id,
                snapshot_time=snapshot_time,
                holdings_written=holdings_written,
                cash_rows_written=cash_rows_written,
                prices_written=prices_written,
                carry_forward_holdings=carry_forward_holdings,
                carry_forward_cash=carry_forward_cash,
                warning_count=self._warning_count,
                error_count=self._error_count,
                imported_symbols=imported_symbols,
            )

        except Exception as exc:
            self.db.rollback()

            self._create_issue(
                sync_run_id=sync_run.id,
                issue_type="us_csv_import_failed",
                severity="error",
                description=str(exc),
                market="US",
            )
            self.db.commit()

            self._finalize_sync_run(
                sync_run,
                status="failed",
                records_processed=records_processed,
                message=str(exc),
            )
            raise