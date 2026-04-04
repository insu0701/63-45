import type { TopHolding } from "../../types/overview";
import { formatCurrency, formatPercent } from "../../utils/format";

type Props = {
  rows: TopHolding[];
};

export function TopHoldingsTable({ rows }: Props) {
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
        Top Holdings
      </div>

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead style={{ background: "#f9fafb" }}>
          <tr>
            <th style={thStyle}>Symbol</th>
            <th style={thStyle}>Name</th>
            <th style={thStyle}>Sleeve</th>
            <th style={thStyle}>Country</th>
            <th style={thStyle}>Market Value</th>
            <th style={thStyle}>Unrealized P&L</th>
            <th style={thStyle}>Return</th>
            <th style={thStyle}>Weight</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.symbol}>
              <td style={tdStyle}>{row.symbol}</td>
              <td style={tdStyle}>{row.security_name}</td>
              <td style={tdStyle}>{row.sleeve}</td>
              <td style={tdStyle}>{row.country}</td>
              <td style={tdStyle}>{formatCurrency(row.market_value_base)}</td>
              <td style={tdStyle}>{formatCurrency(row.unrealized_pnl_base)}</td>
              <td style={tdStyle}>{formatPercent(row.unrealized_return_pct)}</td>
              <td style={tdStyle}>{formatPercent(row.weight_of_total_nav)}</td>
            </tr>
          ))}
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