from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.adapters.kiwoom.market_data import KiwoomMarketDataAdapter
from backend.app.adapters.kiwoom.normalize import quantize_money
from backend.app.adapters.pricing.yfinance_provider import (
    YFinancePrice,
    YFinancePriceProvider,
)
from backend.app.db.models import DataIssue, HoldingSnapshot, PriceSnapshot, SyncRun
from backend.app.services.valuation_service import ValuationService


@dataclass
class RefreshedPrice:
    price: Decimal
    price_timestamp: datetime
    source_type: str


@dataclass
class PriceSyncResult:
    sync_run_id: int
    snapshot_time: datetime
    holdings_written: int
    prices_written: int
    kr_symbols_priced: int
    us_symbols_priced: int
    carry_forward_symbols: int
    warning_count: int
    error_count: int


class PriceSyncService:
    def __init__(self, db: Session):
        self.db = db
        self.valuation = ValuationService(db)
        self.kr_market_data = KiwoomMarketDataAdapter()
        self.us_provider = YFinancePriceProvider()
        self._warning_count = 0
        self._error_count = 0

    def _create_sync_run(self) -> SyncRun:
        sync_run = SyncRun(
            source_type="prices",
            job_name="price_refresh",
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

    def _dec(self, value) -> Decimal | None:
        if value is None or value == "":
            return None
        return Decimal(str(value))

    def _fetch_price_for_row(self, row: HoldingSnapshot) -> RefreshedPrice | None:
        now = datetime.now(UTC)

        if row.country == "KR" or row.currency == "KRW":
            price = self.kr_market_data.get_current_price(row.symbol)
            if price is None:
                return None
            if price <= 0:
                raise ValueError(f"Non-positive KR price returned for {row.symbol}: {price}")
            return RefreshedPrice(
                price=price,
                price_timestamp=now,
                source_type="kiwoom:ka10001",
        )
        if row.country == "US" or row.currency == "USD":
            us_price: YFinancePrice | None = self.us_provider.get_latest_price(row.symbol)
            if us_price is None:
                return None
            if us_price.price <= 0:
                raise ValueError(f"Non-positive US price returned for {row.symbol}: {us_price.price}")
            return RefreshedPrice(
                price=us_price.price,
                price_timestamp=us_price.price_timestamp,
                source_type="yfinance",
        )
        return None

    def _build_repriced_holding(
        self,
        row: HoldingSnapshot,
        *,
        snapshot_time: datetime,
        source_run_id: int,
        refreshed: RefreshedPrice,
    ) -> HoldingSnapshot:
        quantity = self._dec(row.quantity) or Decimal("0")
        avg_cost_native = self._dec(row.avg_cost_native)
        current_price_native = refreshed.price

        cost_basis_native = self._dec(row.cost_basis_native)
        if cost_basis_native is None and avg_cost_native is not None:
            cost_basis_native = quantity * avg_cost_native

        fx_rate_to_base = self._dec(row.fx_rate_to_base)
        cost_basis_base = self._dec(row.cost_basis_base)

        market_value_native = quantize_money(quantity * current_price_native)

        if cost_basis_base is None and cost_basis_native is not None and fx_rate_to_base is not None:
            cost_basis_base = quantize_money(cost_basis_native * fx_rate_to_base)

        market_value_base = (
            quantize_money(market_value_native * fx_rate_to_base)
            if market_value_native is not None and fx_rate_to_base is not None
            else None
        )

        unrealized_pnl_native = (
            quantize_money(market_value_native - cost_basis_native)
            if market_value_native is not None and cost_basis_native is not None
            else None
        )

        unrealized_return_pct = (
            unrealized_pnl_native / cost_basis_native
            if unrealized_pnl_native is not None
            and cost_basis_native is not None
            and cost_basis_native != 0
            else None
        )

        unrealized_pnl_base = (
            quantize_money(market_value_base - cost_basis_base)
            if market_value_base is not None and cost_basis_base is not None
            else None
        )

        return HoldingSnapshot(
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
            avg_cost_native=avg_cost_native,
            current_price_native=current_price_native,
            cost_basis_native=cost_basis_native,
            market_value_native=market_value_native,
            unrealized_pnl_native=unrealized_pnl_native,
            unrealized_return_pct=unrealized_return_pct,
            fx_rate_to_base=fx_rate_to_base,
            cost_basis_base=cost_basis_base,
            market_value_base=market_value_base,
            unrealized_pnl_base=unrealized_pnl_base,
            price_timestamp=refreshed.price_timestamp,
            source_type=f"price_refresh:{refreshed.source_type}",
            source_run_id=source_run_id,
        )

    def _build_carry_forward_holding(
        self,
        row: HoldingSnapshot,
        *,
        snapshot_time: datetime,
        source_run_id: int,
    ) -> HoldingSnapshot:
        return HoldingSnapshot(
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
            source_type="price_refresh:carry_forward",
            source_run_id=source_run_id,
        )

    def run(self) -> PriceSyncResult:
        sync_run = self._create_sync_run()
        records_processed = 0

        try:
            latest_holdings = self.valuation.get_latest_holdings()
            if not latest_holdings:
                raise RuntimeError("No active holdings snapshot found for price refresh.")

            snapshot_time = datetime.now(UTC)

            quote_cache: dict[tuple[str, str], RefreshedPrice | None] = {}
            kr_symbols_priced = 0
            us_symbols_priced = 0
            carry_forward_keys: set[tuple[str, str]] = set()

            holdings_written = 0
            prices_written = 0

            for row in latest_holdings:
                key = (row.symbol, row.market)

                if key not in quote_cache:
                    refreshed = self._fetch_price_for_row(row)
                    quote_cache[key] = refreshed

                    if refreshed is None:
                        carry_forward_keys.add(key)
                        self._create_issue(
                            sync_run_id=sync_run.id,
                            issue_type="price_refresh_missing_quote",
                            severity="warning",
                            description=(
                                f"Could not refresh price for {row.symbol} ({row.market}). "
                                "Carried forward the previous holding valuation."
                            ),
                            symbol=row.symbol,
                            market=row.market,
                        )
                    else:
                        self.db.add(
                            PriceSnapshot(
                                symbol=row.symbol,
                                market=row.market,
                                currency=row.currency,
                                price=refreshed.price,
                                price_timestamp=refreshed.price_timestamp,
                                source_type=refreshed.source_type,
                            )
                        )
                        prices_written += 1

                        if row.country == "KR":
                            kr_symbols_priced += 1
                        elif row.country == "US":
                            us_symbols_priced += 1

                refreshed = quote_cache[key]

                if refreshed is None:
                    cloned = self._build_carry_forward_holding(
                        row,
                        snapshot_time=snapshot_time,
                        source_run_id=sync_run.id,
                    )
                else:
                    cloned = self._build_repriced_holding(
                        row,
                        snapshot_time=snapshot_time,
                        source_run_id=sync_run.id,
                        refreshed=refreshed,
                    )

                self.db.add(cloned)
                holdings_written += 1

            if prices_written == 0:
                raise RuntimeError("Price refresh completed no successful quotes.")

            self.db.commit()

            records_processed = holdings_written + prices_written
            status = "partial" if carry_forward_keys else "success"
            message = (
                f"Price refresh completed with {len(carry_forward_keys)} carry-forward symbols."
                if carry_forward_keys
                else "Price refresh completed successfully."
            )

            self._finalize_sync_run(
                sync_run,
                status=status,
                records_processed=records_processed,
                message=message,
            )

            return PriceSyncResult(
                sync_run_id=sync_run.id,
                snapshot_time=snapshot_time,
                holdings_written=holdings_written,
                prices_written=prices_written,
                kr_symbols_priced=kr_symbols_priced,
                us_symbols_priced=us_symbols_priced,
                carry_forward_symbols=len(carry_forward_keys),
                warning_count=self._warning_count,
                error_count=self._error_count,
            )

        except Exception as exc:
            self.db.rollback()

            self._create_issue(
                sync_run_id=sync_run.id,
                issue_type="price_refresh_failed",
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