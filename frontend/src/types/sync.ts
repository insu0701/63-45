export type SyncStatusSummary = {
  fresh_source_count: number;
  stale_source_count: number;
  missing_source_count: number;
  open_issue_count: number;
  open_error_count: number;
  open_warning_count: number;
};

export type DataSourceStatusItem = {
  source_key: string;
  label: string;
  status: "fresh" | "stale" | "missing" | string;
  last_timestamp: string | null;
  record_count: number;
  source_type: string | null;
  detail: string;
};

export type SyncRunItem = {
  id: number;
  source_type: string;
  job_name: string;
  started_at: string;
  finished_at: string | null;
  status: string;
  records_processed: number;
  warning_count: number;
  error_count: number;
  message: string | null;
};

export type DataIssueItem = {
  id: number;
  detected_at: string;
  issue_type: string;
  severity: string;
  symbol: string | null;
  market: string | null;
  description: string;
  is_resolved: boolean;
  resolved_at: string | null;
  source_run_id: number | null;
};

export type SyncStatusPayload = {
  summary: SyncStatusSummary;
  sources: DataSourceStatusItem[];
  sync_runs: SyncRunItem[];
  data_issues: DataIssueItem[];
};