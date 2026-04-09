import type { RebalanceCandidateItem } from "../../types/strategy";
import { formatCurrency, formatPercent } from "../../utils/format";

type Props = {
  rows: RebalanceCandidateItem[];
  selectedKey: string | null;
  onSelect: (row: RebalanceCandidateItem) => void;
};

export function RebalanceCandidatesTable({ rows, selectedKey, onSelect }: Props) {
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
        Rebalance Candidates
      </div>

      {rows.length === 0 ? (
        <div style={{ padding: "16px", color: "#6b7280" }}>
          No rebalance candidates above the current threshold.
        </div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ background: "#f9fafb" }}>
              <tr>
                <th style={thStyle}>Symbol</th>
                <th style={thStyle}>Sleeve</th>
                <th style={thStyle}>Action</th>
                <th style={thStyle}>Current $</th>
                <th style={thStyle}>Target $</th>
                <th style={thStyle}>Delta</th>
                <th style={thStyle}>Abs Delta</th>
                <th style={thStyle}>Current Wt</th>
                <th style={thStyle}>Target Wt</th>
                <th style={thStyle}>Reason</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const rowKey = `${row.symbol}::${row.sleeve}`;
                const isSelected = rowKey === selectedKey;

                return (
                  <tr
                    key={rowKey}
                    onClick={() => onSelect(row)}
                    style={{
                      background: isSelected ? "#eff6ff" : "white",
                      cursor: "pointer",
                    }}
                  >
                    <td style={tdStyle}>{row.symbol}</td>
                    <td style={tdStyle}>{row.sleeve}</td>
                    <td style={tdStyle}>{row.suggested_action}</td>
                    <td style={tdStyle}>{formatCurrency(row.current_market_value_base, "USD", 0)}</td>
                    <td style={tdStyle}>{formatCurrency(row.target_dollars, "USD", 0)}</td>
                    <td style={tdStyle}>{formatCurrency(row.actual_vs_target_delta, "USD", 0)}</td>
                    <td style={tdStyle}>{formatCurrency(row.abs_delta_dollars, "USD", 0)}</td>
                    <td style={tdStyle}>{formatPercent(row.current_weight_of_nav, 2)}</td>
                    <td style={tdStyle}>
                      {row.target_weight == null ? "—" : formatPercent(row.target_weight, 2)}
                    </td>
                    <td style={tdStyle}>{row.reason_code ?? "—"}</td>
                  </tr>
                );
              })}
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