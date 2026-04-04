import type { Concentration } from "../../types/overview";
import { formatPercent } from "../../utils/format";

type Props = {
  data: Concentration;
};

export function ConcentrationPanel({ data }: Props) {
  const rows = [
    { label: "Top 1 Position", value: data.top1_pct },
    { label: "Top 3 Positions", value: data.top3_pct },
    { label: "Top 5 Positions", value: data.top5_pct },
    { label: "Largest Sector", value: data.largest_sector_pct },
    { label: "Largest Sleeve", value: data.largest_sleeve_pct },
  ];

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
        Concentration
      </div>

      <div style={{ padding: "8px 16px 16px" }}>
        {rows.map((row) => (
          <div
            key={row.label}
            style={{
              display: "flex",
              justifyContent: "space-between",
              padding: "12px 0",
              borderBottom: "1px solid #f3f4f6",
            }}
          >
            <span style={{ color: "#6b7280" }}>{row.label}</span>
            <strong>{formatPercent(row.value)}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}