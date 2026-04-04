from pydantic import BaseModel


class DataSourceStatusItem(BaseModel):
    source_key: str
    label: str
    status: str
    last_timestamp: str | None
    record_count: int
    source_type: str | None
    detail: str


class SyncRunItem(BaseModel):
    id: int
    source_type: str
    job_name: str
    started_at: str
    finished_at: str | None
    status: str
    records_processed: int
    warning_count: int
    error_count: int
    message: str | None


class DataIssueItem(BaseModel):
    id: int
    detected_at: str
    issue_type: str
    severity: str
    symbol: str | None
    market: str | None
    description: str
    is_resolved: bool
    resolved_at: str | None
    source_run_id: int | None


class SyncStatusSummaryItem(BaseModel):
    fresh_source_count: int
    stale_source_count: int
    missing_source_count: int
    open_issue_count: int
    open_error_count: int
    open_warning_count: int