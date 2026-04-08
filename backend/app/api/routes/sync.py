from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.response import build_response
from backend.app.services.health_service import HealthService
from backend.app.services.sync.kiwoom_sync_service import KiwoomSyncService

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])


@router.get("/status")
def get_sync_status(
    sync_run_limit: int = Query(default=20, ge=1, le=100),
    data_issue_limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = HealthService(db)

    summary = service.get_summary()
    source_statuses = service.get_data_source_statuses()
    sync_runs = service.get_recent_sync_runs(limit=sync_run_limit)
    data_issues = service.get_open_data_issues(limit=data_issue_limit)
    snapshot_time = service.get_latest_relevant_timestamp()

    data = {
        "summary": {
            "fresh_source_count": summary.fresh_source_count,
            "stale_source_count": summary.stale_source_count,
            "missing_source_count": summary.missing_source_count,
            "open_issue_count": summary.open_issue_count,
            "open_error_count": summary.open_error_count,
            "open_warning_count": summary.open_warning_count,
        },
        "sources": [
            {
                "source_key": row.source_key,
                "label": row.label,
                "status": row.status,
                "last_timestamp": row.last_timestamp.isoformat() if row.last_timestamp else None,
                "record_count": row.record_count,
                "source_type": row.source_type,
                "detail": row.detail,
            }
            for row in source_statuses
        ],
        "sync_runs": [
            {
                "id": row.id,
                "source_type": row.source_type,
                "job_name": row.job_name,
                "started_at": row.started_at.isoformat(),
                "finished_at": row.finished_at.isoformat() if row.finished_at else None,
                "status": row.status,
                "records_processed": row.records_processed,
                "warning_count": row.warning_count,
                "error_count": row.error_count,
                "message": row.message,
            }
            for row in sync_runs
        ],
        "data_issues": [
            {
                "id": row.id,
                "detected_at": row.detected_at.isoformat(),
                "issue_type": row.issue_type,
                "severity": row.severity,
                "symbol": row.symbol,
                "market": row.market,
                "description": row.description,
                "is_resolved": row.is_resolved,
                "resolved_at": row.resolved_at.isoformat() if row.resolved_at else None,
                "source_run_id": row.source_run_id,
            }
            for row in data_issues
        ],
    }

    return build_response(data=data, snapshot_time=snapshot_time)

@router.post("/kiwoom")
def run_kiwoom_sync(db: Session = Depends(get_db)):
    service = KiwoomSyncService(db)
    result = service.run()

    data = {
        "sync_run_id": result.sync_run_id,
        "snapshot_time": result.snapshot_time.isoformat(),
        "holdings_written": result.holdings_written,
        "cash_rows_written": result.cash_rows_written,
        "prices_written": result.prices_written,
        "carry_forward_holdings": result.carry_forward_holdings,
        "carry_forward_cash": result.carry_forward_cash,
        "warning_count": result.warning_count,
        "error_count": result.error_count,
        "archive_paths": result.archive_paths,
    }

    return build_response(data=data, snapshot_time=result.snapshot_time)