from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.adapters.kiwoom.account import KiwoomAccountAdapter
from backend.app.adapters.kiwoom.archive import archive_kiwoom_payload
from backend.app.adapters.kiwoom.normalize import (
    normalize_holdings_payload,
    normalize_krw_cash_payload,
)
from backend.app.core.config import settings
from backend.app.db.models import (
    Account,
    CashBalanceSnapshot,
    DataIssue,
    FxRateSnapshot,
    HoldingSnapshot,
    PriceSnapshot,
    SyncRun,
)


@dataclass
class KiwoomSyncResult:
    sync_run_id: int
    snapshot_time: datetime
    holdings_written: int
    cash_rows_written: int
    prices_written: int
    carry_forward_holdings: int
    carry_forward_cash: int
    warning_count: int
    error_count: int
    archive_paths: dict[str, str]


class KiwoomSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.adapter = KiwoomAccountAdapter()
        self._warning_count = 0
        self._error_count = 0

    def _create_sync_run(self) -> SyncRun:
        sync_run = SyncRun(
            source_type="kiwoom",
            job_name="kiwoom_read_only_sync",
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

    def _get_or_create_kiwoom_kr_account(self) -> Account:
        stmt = (
            select(Account)
            .where(Account.broker_name == "Kiwoom")
            .where(Account.account_label == "Kiwoom KR")
            .limit(1)
        )
        account = self.db.scalar(stmt)

        if account is not None:
            return account

        account = Account(
            broker_name="Kiwoom",
            account_label="Kiwoom KR",
            market_scope="KR",
            base_currency=settings.base_currency,
            is_active=True,
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def _get_latest_krw_to_base_fx(self) -> tuple[Decimal, datetime]:
        stmt = (
            select(FxRateSnapshot)
            .where(FxRateSnapshot.base_currency == "KRW")
            .where(FxRateSnapshot.quote_currency == settings.base_currency)
            .order_by(FxRateSnapshot.rate_timestamp.desc())
            .limit(1)
        )
        fx_row = self.db.scalar(stmt)

        if fx_row is None or fx_row.rate is None or fx_row.rate_timestamp is None:
            raise RuntimeError("No KRW -> base FX snapshot found. Sync FX before Kiwoom sync.")

        return Decimal(fx_row.rate), fx_row.rate_timestamp

    def _latest_holdings_snapshot_time(self) -> datetime | None:
        stmt = select(HoldingSnapshot.snapshot_time).order_by(HoldingSnapshot.snapshot_time.desc()).limit(1)
        return self.db.scalar(stmt)

    def _latest_cash_snapshot_time(self) -> datetime | None:
        stmt = select(CashBalanceSnapshot.snapshot_time).order_by(CashBalanceSnapshot.snapshot_time.desc()).limit(1)
        return self.db.scalar(stmt)

    def _carry_forward_non_kr_holdings(self, snapshot_time: datetime, sync_run_id: int) -> int:
        latest_ts = self._latest_holdings_snapshot_time()
        if latest_ts is None:
            return 0

        rows = self.db.scalars(
            select(HoldingSnapshot)
            .where(HoldingSnapshot.snapshot_time == latest_ts)
            .where(HoldingSnapshot.sleeve != "KR")
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

    def _carry_forward_non_krw_cash(self, snapshot_time: datetime, sync_run_id: int) -> int:
        latest_ts = self._latest_cash_snapshot_time()
        if latest_ts is None:
            return 0

        rows = self.db.scalars(
            select(CashBalanceSnapshot)
            .where(CashBalanceSnapshot.snapshot_time == latest_ts)
            .where(CashBalanceSnapshot.currency != "KRW")
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

    def run(self) -> KiwoomSyncResult:
        sync_run = self._create_sync_run()
        records_processed = 0

        try:
            cash_envelope = self.adapter.get_cash_raw()
            daily_status_envelope = self.adapter.get_daily_status_raw()
            holdings_payload = self.adapter.get_holdings_raw()

            cash_archive = archive_kiwoom_payload("cash", cash_envelope.body)
            daily_status_archive = archive_kiwoom_payload("daily_status", daily_status_envelope.body)
            holdings_archive = archive_kiwoom_payload("holdings", holdings_payload)

            if cash_envelope.body.get("return_code") != 0:
                raise RuntimeError(f"Kiwoom cash fetch failed: {cash_envelope.body.get('return_msg')}")

            first_page_body = holdings_payload["pages"][0]["body"] if holdings_payload.get("pages") else {}
            if first_page_body.get("return_code") != 0:
                raise RuntimeError(f"Kiwoom holdings fetch failed: {first_page_body.get('return_msg')}")

            fx_rate_to_base, fx_timestamp = self._get_latest_krw_to_base_fx()

            if datetime.now(UTC) - fx_timestamp.replace(tzinfo=UTC) > timedelta(hours=72):
                self._create_issue(
                    sync_run_id=sync_run.id,
                    issue_type="stale_fx_snapshot",
                    severity="warning",
                    description="Latest KRW -> base FX snapshot is older than 72 hours.",
                )

            account = self._get_or_create_kiwoom_kr_account()
            snapshot_time = datetime.now(UTC)

            carry_forward_holdings = self._carry_forward_non_kr_holdings(snapshot_time, sync_run.id)
            carry_forward_cash = self._carry_forward_non_krw_cash(snapshot_time, sync_run.id)

            normalized_cash = normalize_krw_cash_payload(
                cash_envelope.body,
                fx_rate_to_base=fx_rate_to_base,
            )

            totals, normalized_holdings = normalize_holdings_payload(
                holdings_payload,
                fx_rate_to_base=fx_rate_to_base,
            )

            if not normalized_holdings:
                self._create_issue(
                    sync_run_id=sync_run.id,
                    issue_type="empty_kiwoom_holdings",
                    severity="warning",
                    description="Kiwoom holdings payload returned no holdings rows.",
                )

            cash_row = CashBalanceSnapshot(
                account_id=account.id,
                snapshot_time=snapshot_time,
                currency=normalized_cash.currency,
                amount_native=normalized_cash.amount_native,
                fx_rate_to_base=normalized_cash.fx_rate_to_base,
                amount_base=normalized_cash.amount_base,
                source_type="kiwoom:kt00001",
                source_run_id=sync_run.id,
            )
            self.db.add(cash_row)
            cash_rows_written = 1

            holdings_written = 0
            prices_written = 0

            sum_cost_basis_native = Decimal("0")
            sum_market_value_native = Decimal("0")

            for row in normalized_holdings:
                holding = HoldingSnapshot(
                    account_id=account.id,
                    snapshot_time=snapshot_time,
                    symbol=row.symbol,
                    security_name=row.security_name,
                    market="KRX",
                    country="KR",
                    sleeve="KR",
                    sector=None,
                    industry=None,
                    currency="KRW",
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
                    price_timestamp=snapshot_time,
                    source_type="kiwoom:kt00018",
                    source_run_id=sync_run.id,
                )
                self.db.add(holding)
                holdings_written += 1

                if row.current_price_native is not None:
                    price = PriceSnapshot(
                        symbol=row.symbol,
                        market="KRX",
                        currency="KRW",
                        price=row.current_price_native,
                        price_timestamp=snapshot_time,
                        source_type="kiwoom:kt00018",
                    )
                    self.db.add(price)
                    prices_written += 1

                if row.cost_basis_native is not None:
                    sum_cost_basis_native += row.cost_basis_native
                if row.market_value_native is not None:
                    sum_market_value_native += row.market_value_native

            reported_cost_basis = totals.get("tot_pur_amt")
            reported_market_value = totals.get("tot_evlt_amt")

            if reported_cost_basis is not None and abs(sum_cost_basis_native - reported_cost_basis) > Decimal("1"):
                self._create_issue(
                    sync_run_id=sync_run.id,
                    issue_type="holdings_total_cost_mismatch",
                    severity="warning",
                    description=(
                        f"Sum of normalized holding cost basis ({sum_cost_basis_native}) "
                        f"does not match Kiwoom reported tot_pur_amt ({reported_cost_basis})."
                    ),
                )

            if reported_market_value is not None and abs(sum_market_value_native - reported_market_value) > Decimal("1"):
                self._create_issue(
                    sync_run_id=sync_run.id,
                    issue_type="holdings_total_market_value_mismatch",
                    severity="warning",
                    description=(
                        f"Sum of normalized holding market values ({sum_market_value_native}) "
                        f"does not match Kiwoom reported tot_evlt_amt ({reported_market_value})."
                    ),
                )

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
                message="Kiwoom KR sync completed successfully.",
            )

            return KiwoomSyncResult(
                sync_run_id=sync_run.id,
                snapshot_time=snapshot_time,
                holdings_written=holdings_written,
                cash_rows_written=cash_rows_written,
                prices_written=prices_written,
                carry_forward_holdings=carry_forward_holdings,
                carry_forward_cash=carry_forward_cash,
                warning_count=self._warning_count,
                error_count=self._error_count,
                archive_paths={
                    "cash": str(cash_archive),
                    "daily_status": str(daily_status_archive),
                    "holdings": str(holdings_archive),
                },
            )

        except Exception as exc:
            self.db.rollback()

            self._create_issue(
                sync_run_id=sync_run.id,
                issue_type="kiwoom_sync_failed",
                severity="error",
                description=str(exc),
            )
            self.db.commit()

            self._finalize_sync_run(
                sync_run,
                status="failed",
                records_processed=records_processed,
                message=str(exc),
            )
            raise