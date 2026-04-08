from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, ROUND_HALF_UP

import httpx
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.models import DataIssue, FxRateSnapshot, SyncRun


FX_QUANT = Decimal("0.000000000001")
RECIPROCAL_QUANT = Decimal("0.000001")


@dataclass
class FxSyncResult:
    sync_run_id: int
    snapshot_time: datetime
    rates_written: int
    warning_count: int
    error_count: int
    provider: str


class FxSyncService:
    def __init__(self, db: Session):
        self.db = db
        self._warning_count = 0
        self._error_count = 0

    def _create_sync_run(self) -> SyncRun:
        sync_run = SyncRun(
            source_type="fx",
            job_name="fx_refresh",
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
    ) -> None:
        issue = DataIssue(
            detected_at=datetime.now(UTC),
            issue_type=issue_type,
            severity=severity,
            symbol=None,
            market=None,
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

    def _extract_krw_per_base(self, body: object) -> Decimal:
        # Frankfurter v2 /rates example uses data[0].rate, so support the
        # current list-shaped response first.
        if isinstance(body, list):
            if not body:
                raise RuntimeError("FX provider returned an empty list response.")

            first = body[0]
            if not isinstance(first, dict) or "rate" not in first:
                raise RuntimeError("FX provider returned an unexpected list response shape.")

            value = Decimal(str(first["rate"]))
            if value <= 0:
                raise RuntimeError("Received non-positive FX rate from provider.")
            return value

        # Backward-compatible fallback if provider shape changes or an older
        # response format is returned.
        if isinstance(body, dict):
            rates = body.get("rates")
            if isinstance(rates, dict) and "KRW" in rates:
                value = Decimal(str(rates["KRW"]))
                if value <= 0:
                    raise RuntimeError("Received non-positive FX rate from provider.")
                return value

        raise RuntimeError("Unrecognized FX provider response shape.")

    def _fetch_krw_to_base_rate(self) -> Decimal:
        base_currency = settings.base_currency.upper()

        url = (
            f"https://api.frankfurter.dev/v2/rates"
            f"?base={base_currency}&quotes=KRW"
        )

        response = httpx.get(url, timeout=15)
        response.raise_for_status()
        body = response.json()

        krw_per_base = self._extract_krw_per_base(body)

        # Store in app-native direction:
        # base_currency='KRW', quote_currency='USD' => 1 KRW = ? USD
        base_per_krw = (Decimal("1") / krw_per_base).quantize(
            FX_QUANT,
            rounding=ROUND_HALF_UP,
        )
        return base_per_krw

    def run(self) -> FxSyncResult:
        sync_run = self._create_sync_run()
        records_processed = 0

        try:
            base_currency = settings.base_currency.upper()
            snapshot_time = datetime.now(UTC)

            krw_to_base = self._fetch_krw_to_base_rate()

            row_krw_to_base = FxRateSnapshot(
                base_currency="KRW",
                quote_currency=base_currency,
                rate=krw_to_base,
                rate_timestamp=snapshot_time,
                source_type="frankfurter",
            )
            self.db.add(row_krw_to_base)

            rates_written = 1

            if base_currency != "KRW":
                base_to_krw = (Decimal("1") / krw_to_base).quantize(
                    RECIPROCAL_QUANT,
                    rounding=ROUND_HALF_UP,
                )

                row_base_to_krw = FxRateSnapshot(
                    base_currency=base_currency,
                    quote_currency="KRW",
                    rate=base_to_krw,
                    rate_timestamp=snapshot_time,
                    source_type="frankfurter",
                )
                self.db.add(row_base_to_krw)
                rates_written = 2

            self.db.commit()
            records_processed = rates_written

            self._finalize_sync_run(
                sync_run,
                status="success",
                records_processed=records_processed,
                message="FX refresh completed successfully.",
            )

            return FxSyncResult(
                sync_run_id=sync_run.id,
                snapshot_time=snapshot_time,
                rates_written=rates_written,
                warning_count=self._warning_count,
                error_count=self._error_count,
                provider="frankfurter",
            )

        except Exception as exc:
            self.db.rollback()

            self._create_issue(
                sync_run_id=sync_run.id,
                issue_type="fx_sync_failed",
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