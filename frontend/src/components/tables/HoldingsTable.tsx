import type { HoldingListItem } from "../../types/holdings";
import { formatCurrency, formatPercent } from "../../utils/format";

type Props = {
  rows: HoldingListItem[];
  selectedSymbol: string | null;
  onSelect: (symbol: string) => void;
};

export function HoldingsTable({ rows, selectedSymbol, onSelect }: Props) {
  return (
    <div
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        overflow: "hidden",
        background: "white",
      }}
    >
      <div style={{ padding: "16px", fontWeight: 700, borderBottom: "1px solid #e5e7eb" }}>
        Holdings
      </div>

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead style={{ background: "#f9fafb" }}>
          <tr>
            <th style={thStyle}>Symbol</th>
            <th style={thStyle}>Name</th>
            <th style={thStyle}>Sleeve</th>
            <th style={thStyle}>Sector</th>
            <th style={thStyle}>Quantity</th>
            <th style={thStyle}>Market Value</th>
            <th style={thStyle}>Unrealized P&L</th>
            <th style={thStyle}>Return</th>
            <th style={thStyle}>Weight</th>
          </tr>
        </thead>

        <tbody>
          {rows.map((row) => {
            const isSelected = selectedSymbol === row.symbol;

            return (
              <tr
                key={row.symbol}
                onClick={() => onSelect(row.symbol)}
                style={{
                  cursor: "pointer",
                  background: isSelected ? "#eff6ff" : "white",
                }}
              >
                <td style={tdStyle}>{row.symbol}</td>
                <td style={tdStyle}>{row.security_name}</td>
                <td style={tdStyle}>{row.sleeve}</td>
                <td style={tdStyle}>{row.sector ?? "Unknown"}</td>
                <td style={tdStyle}>{row.quantity}</td>
                <td style={tdStyle}>
                  {row.market_value_base != null ? formatCurrency(row.market_value_base) : "N/A"}
                </td>
                <td style={tdStyle}>
                  {row.unrealized_pnl_base != null ? formatCurrency(row.unrealized_pnl_base) : "N/A"}
                </td>
                <td style={tdStyle}>
                  {row.unrealized_return_pct != null ? formatPercent(row.unrealized_return_pct) : "N/A"}
                </td>
                <td style={tdStyle}>{formatPercent(row.weight_of_total_nav)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
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