import type { DataIssueItem } from "../../types/sync";
import { formatTimestamp } from "../../utils/format";

type Props = {
  rows: DataIssueItem[];
};

export function DataIssuesTable({ rows }: Props) {
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
        Open Data Issues
      </div>

      {rows.length === 0 ? (
        <div style={{ padding: "16px", color: "#6b7280" }}>No open data issues.</div>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ background: "#f9fafb" }}>
            <tr>
              <th style={thStyle}>Detected</th>
              <th style={thStyle}>Severity</th>
              <th style={thStyle}>Type</th>
              <th style={thStyle}>Symbol</th>
              <th style={thStyle}>Market</th>
              <th style={thStyle}>Description</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                <td style={tdStyle}>{formatTimestamp(row.detected_at)}</td>
                <td style={tdStyle}>{row.severity}</td>
                <td style={tdStyle}>{row.issue_type}</td>
                <td style={tdStyle}>{row.symbol ?? "-"}</td>
                <td style={tdStyle}>{row.market ?? "-"}</td>
                <td style={tdStyle}>{row.description}</td>
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