import type { DailyDecisionLogItem } from "../../types/strategy";
import { formatCurrency, formatTimestamp } from "../../utils/format";

type Props = {
  rows: DailyDecisionLogItem[];
};

export function DailyDecisionLogTable({ rows }: Props) {
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
        Daily Decision Log
      </div>

      {rows.length === 0 ? (
        <div style={{ padding: "16px", color: "#6b7280" }}>No daily decision log rows found.</div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ background: "#f9fafb" }}>
              <tr>
                <th style={thStyle}>Decision Date</th>
                <th style={thStyle}>Symbol</th>
                <th style={thStyle}>Sleeve</th>
                <th style={thStyle}>Current State</th>
                <th style={thStyle}>Target State</th>
                <th style={thStyle}>Current $</th>
                <th style={thStyle}>Target $</th>
                <th style={thStyle}>Order Qty</th>
                <th style={thStyle}>Fill Qty</th>
                <th style={thStyle}>Reason</th>
                <th style={thStyle}>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={`${row.symbol}-${row.decision_date}-${index}`}>
                  <td style={tdStyle}>{row.decision_date}</td>
                  <td style={tdStyle}>{row.symbol}</td>
                  <td style={tdStyle}>{row.sleeve}</td>
                  <td style={tdStyle}>{row.current_state ?? "—"}</td>
                  <td style={tdStyle}>{row.target_state ?? "—"}</td>
                  <td style={tdStyle}>
                    {row.current_position_dollars == null
                      ? "—"
                      : formatCurrency(row.current_position_dollars, "USD", 0)}
                  </td>
                  <td style={tdStyle}>
                    {row.target_position_dollars == null
                      ? "—"
                      : formatCurrency(row.target_position_dollars, "USD", 0)}
                  </td>
                  <td style={tdStyle}>{row.generated_order_quantity ?? "—"}</td>
                  <td style={tdStyle}>{row.fill_quantity ?? "—"}</td>
                  <td style={tdStyle}>{row.reason_code ?? "—"}</td>
                  <td style={tdStyle}>{formatTimestamp(row.decision_timestamp)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
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
  whiteSpace: "nowrap",
};

const tdStyle: React.CSSProperties = {
  padding: "12px 16px",
  borderBottom: "1px solid #f3f4f6",
  fontSize: "14px",
  whiteSpace: "nowrap",
};