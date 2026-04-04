import { formatCurrency, formatPercent } from "../../utils/format";

type Row = {
  label: string;
  marketValueBase?: number;
  totalBaseValue?: number;
  weightOfTotalNav: number;
  extra?: string;
};

type Props = {
  title: string;
  rows: Row[];
  valueLabel?: string;
};

export function AllocationTable({ title, rows, valueLabel = "Value" }: Props) {
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
        {title}
      </div>

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead style={{ background: "#f9fafb" }}>
          <tr>
            <th style={thStyle}>Label</th>
            <th style={thStyle}>{valueLabel}</th>
            <th style={thStyle}>Weight</th>
            <th style={thStyle}>Extra</th>
          </tr>
        </thead>

        <tbody>
          {rows.map((row) => {
            const value =
              row.marketValueBase != null
                ? row.marketValueBase
                : row.totalBaseValue != null
                ? row.totalBaseValue
                : 0;

            return (
              <tr key={row.label}>
                <td style={tdStyle}>{row.label}</td>
                <td style={tdStyle}>{formatCurrency(value)}</td>
                <td style={tdStyle}>{formatPercent(row.weightOfTotalNav)}</td>
                <td style={tdStyle}>{row.extra ?? "-"}</td>
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