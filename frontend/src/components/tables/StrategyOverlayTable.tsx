import type { StrategyOverlayItem } from "../../types/strategy";
import { formatCurrency, formatPercent } from "../../utils/format";

type Props = {
  rows: StrategyOverlayItem[];
  selectedKey: string | null;
  onSelect: (row: StrategyOverlayItem) => void;
};

export function StrategyOverlayTable({ rows, selectedKey, onSelect }: Props) {
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
        Actual vs Target Overlay
      </div>

      {rows.length === 0 ? (
        <div style={{ padding: "16px", color: "#6b7280" }}>No strategy overlay rows found.</div>
      ) : (
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead style={{ background: "#f9fafb" }}>
              <tr>
                <th style={thStyle}>Symbol</th>
                <th style={thStyle}>Sleeve</th>
                <th style={thStyle}>Current MV</th>
                <th style={thStyle}>Current Wt</th>
                <th style={thStyle}>Strategy State</th>
                <th style={thStyle}>Target State</th>
                <th style={thStyle}>Target $</th>
                <th style={thStyle}>Delta</th>
                <th style={thStyle}>Eligibility</th>
                <th style={thStyle}>Buy List</th>
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
                    <td style={tdStyle}>{formatCurrency(row.current_market_value_base, "USD", 0)}</td>
                    <td style={tdStyle}>{formatPercent(row.current_weight_of_nav, 2)}</td>
                    <td style={tdStyle}>{row.strategy_state ?? "—"}</td>
                    <td style={tdStyle}>{row.target_state ?? "—"}</td>
                    <td style={tdStyle}>
                      {row.target_dollars == null ? "—" : formatCurrency(row.target_dollars, "USD", 0)}
                    </td>
                    <td style={tdStyle}>
                      {row.actual_vs_target_delta == null
                        ? "—"
                        : formatCurrency(row.actual_vs_target_delta, "USD", 0)}
                    </td>
                    <td style={tdStyle}>{row.eligibility_status ?? "—"}</td>
                    <td style={tdStyle}>{row.buy_list_status ?? "—"}</td>
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