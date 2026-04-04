import type { SyncRunItem } from "../../types/sync";
import { formatTimestamp } from "../../utils/format";

type Props = {
  rows: SyncRunItem[];
};

export function SyncRunsTable({ rows }: Props) {
  return (
    <div
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        background: "white",
        overflow: "hidden",
      }}
    >
      <div style={{ padding: "16px", fontWeight: 700, borderBottom: "1px solid #e5e7eb" }}>
        Sync Runs
      </div>

      {rows.length === 0 ? (
        <div style={{ padding: "16px", color: "#6b7280" }}>No sync runs yet.</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ background: "#f9fafb" }}>
            <tr>
              <th style={thStyle}>Job</th>
              <th style={thStyle}>Source</th>
              <th style={thStyle}>Status</th>
              <th style={thStyle}>Started</th>
              <th style={thStyle}>Finished</th>
              <th style={thStyle}>Records</th>
              <th style={thStyle}>Warnings</th>
              <th style={thStyle}>Errors</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td style={tdStyle}>{row.job_name}</td>
                <td style={tdStyle}>{row.source_type}</td>
                <td style={tdStyle}>{row.status}</td>
                <td style={tdStyle}>{formatTimestamp(row.started_at)}</td>
                <td style={tdStyle}>{formatTimestamp(row.finished_at)}</td>
                <td style={tdStyle}>{row.records_processed}</td>
                <td style={tdStyle}>{row.warning_count}</td>
                <td style={tdStyle}>{row.error_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

const thStyle: React.CSSProperties = {
  textAlign: "left",
  padding: "12px 16px",
  fontSize: "13px",
  color: "#6b7280",
  borderBottom: "1px solid #e5e7eb",
};

const tdStyle: React.CSSProperties = {
  padding: "12px 16px",
  borderBottom: "1px solid #f3f4f6",
  fontSize: "14px",
};