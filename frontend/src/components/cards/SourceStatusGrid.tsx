import type { DataSourceStatusItem } from "../../types/sync";
import { formatTimestamp } from "../../utils/format";

type Props = {
  rows: DataSourceStatusItem[];
};

export function SourceStatusGrid({ rows }: Props) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
        gap: "16px",
      }}
    >
      {rows.map((row) => (
        <div
          key={row.source_key}
          style={{
            border: "1px solid #e5e7eb",
            borderRadius: "12px",
            background: "white",
            padding: "16px",
            boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
            <strong>{row.label}</strong>
            <StatusBadge status={row.status} />
          </div>

          <div style={{ display: "grid", gap: "8px", fontSize: "14px" }}>
            <Row label="Last timestamp" value={formatTimestamp(row.last_timestamp)} />
            <Row label="Record count" value={String(row.record_count)} />
            <Row label="Source type" value={row.source_type ?? "N/A"} />
            <Row label="Detail" value={row.detail} />
          </div>
        </div>
      ))}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, React.CSSProperties> = {
    fresh: {
      background: "#dcfce7",
      color: "#166534",
      border: "1px solid #bbf7d0",
    },
    stale: {
      background: "#fef3c7",
      color: "#92400e",
      border: "1px solid #fde68a",
    },
    missing: {
      background: "#fee2e2",
      color: "#991b1b",
      border: "1px solid #fecaca",
    },
  };

  return (
    <span
      style={{
        padding: "4px 10px",
        borderRadius: "999px",
        fontSize: "12px",
        fontWeight: 700,
        textTransform: "uppercase",
        ...(styles[status] ?? {
          background: "#e5e7eb",
          color: "#374151",
          border: "1px solid #d1d5db",
        }),
      }}
    >
      {status}
    </span>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: "12px" }}>
      <span style={{ color: "#6b7280" }}>{label}</span>
      <span style={{ textAlign: "right" }}>{value}</span>
    </div>
  );
}