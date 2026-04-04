from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models import (
    CashBalanceSnapshot,
    DataIssue,
    FxRateSnapshot,
    HoldingSnapshot,
    PriceSnapshot,
    SyncRun,
)


@dataclass
class DataSourceStatus:
    source_key: str
    label: str
    status: str
    last_timestamp: datetime | None
    record_count: int
    source_type: str | None
    detail: str


@dataclass
class SyncStatusSummary:
    fresh_source_count: int
    stale_source_count: int
    missing_source_count: int
    open_issue_count: int
    open_error_count: int
    open_warning_count: int


class HealthService:
    def __init__(self, db: Session):
        self.db = db

    def _normalize_dt(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)

    def _latest_timestamp_and_count(self, model, ts_column):
        latest_timestamp = self.db.scalar(
            select(func.max(ts_column)).select_from(model)
        )

        if latest_timestamp is None:
            return None, 0

        record_count = self.db.scalar(
            select(func.count()).select_from(model).where(ts_column == latest_timestamp)
        ) or 0

        return latest_timestamp, int(record_count)

    def _latest_source_type(self, model, ts_column, source_column):
        latest_timestamp = self.db.scalar(
            select(func.max(ts_column)).select_from(model)
        )

        if latest_timestamp is None:
            return None

        return self.db.scalar(
            select(source_column)
            .where(ts_column == latest_timestamp)
            .limit(1)
        )

    def _status_from_timestamp(self, value: datetime | None, freshness_hours: int) -> tuple[str, str]:
        value = self._normalize_dt(value)

        if value is None:
            return "missing", "No data found"

        now = datetime.now(UTC)
        age_hours = (now - value).total_seconds() / 3600

        if age_hours <= freshness_hours:
            return "fresh", f"{age_hours:.1f}h old"

        return "stale", f"{age_hours:.1f}h old"

    def get_data_source_statuses(self) -> list[DataSourceStatus]:
        definitions = [
            {
                "source_key": "holdings",
                "label": "Holdings Snapshots",
                "model": HoldingSnapshot,
                "ts_column": HoldingSnapshot.snapshot_time,
                "source_column": HoldingSnapshot.source_type,
                "freshness_hours": 24,
            },
            {
                "source_key": "cash",
                "label": "Cash Snapshots",
                "model": CashBalanceSnapshot,
                "ts_column": CashBalanceSnapshot.snapshot_time,
                "source_column": CashBalanceSnapshot.source_type,
                "freshness_hours": 24,
            },
            {
                "source_key": "prices",
                "label": "Price Snapshots",
                "model": PriceSnapshot,
                "ts_column": PriceSnapshot.price_timestamp,
                "source_column": PriceSnapshot.source_type,
                "freshness_hours": 24,
            },
            {
                "source_key": "fx",
                "label": "FX Snapshots",
                "model": FxRateSnapshot,
                "ts_column": FxRateSnapshot.rate_timestamp,
                "source_column": FxRateSnapshot.source_type,
                "freshness_hours": 24,
            },
        ]

        rows: list[DataSourceStatus] = []

        for definition in definitions:
            latest_timestamp, record_count = self._latest_timestamp_and_count(
                definition["model"],
                definition["ts_column"],
            )
            source_type = self._latest_source_type(
                definition["model"],
                definition["ts_column"],
                definition["source_column"],
            )
            status, detail = self._status_from_timestamp(
                latest_timestamp,
                definition["freshness_hours"],
            )

            rows.append(
                DataSourceStatus(
                    source_key=definition["source_key"],
                    label=definition["label"],
                    status=status,
                    last_timestamp=self._normalize_dt(latest_timestamp),
                    record_count=record_count,
                    source_type=source_type,
                    detail=detail,
                )
            )

        return rows

    def get_recent_sync_runs(self, limit: int = 20) -> list[SyncRun]:
        stmt = (
            select(SyncRun)
            .order_by(SyncRun.started_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_open_data_issues(self, limit: int = 50) -> list[DataIssue]:
        stmt = (
            select(DataIssue)
            .where(DataIssue.is_resolved.is_(False))
            .order_by(DataIssue.detected_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_summary(self) -> SyncStatusSummary:
        source_statuses = self.get_data_source_statuses()
        issues = self.get_open_data_issues(limit=1000)

        fresh_source_count = sum(1 for row in source_statuses if row.status == "fresh")
        stale_source_count = sum(1 for row in source_statuses if row.status == "stale")
        missing_source_count = sum(1 for row in source_statuses if row.status == "missing")

        open_issue_count = len(issues)
        open_error_count = sum(1 for row in issues if row.severity == "error")
        open_warning_count = sum(1 for row in issues if row.severity == "warning")

        return SyncStatusSummary(
            fresh_source_count=fresh_source_count,
            stale_source_count=stale_source_count,
            missing_source_count=missing_source_count,
            open_issue_count=open_issue_count,
            open_error_count=open_error_count,
            open_warning_count=open_warning_count,
        )

    def get_latest_relevant_timestamp(self) -> datetime | None:
        timestamps = [row.last_timestamp for row in self.get_data_source_statuses() if row.last_timestamp is not None]
        if not timestamps:
            return None
        return max(timestamps)