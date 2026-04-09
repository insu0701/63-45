import type { OverviewSnapshotMetadata } from "../../types/overview";
import { formatTimestamp } from "../../utils/format";

type Props = {
  data: OverviewSnapshotMetadata;
};

export function SnapshotMetadataPanel({ data }: Props) {
  const rows = [
    {
      label: "Holdings Snapshot",
      timestamp: data.holdings_snapshot_time,
      sourceType: data.holdings_source_type,
      detail: data.holdings_detail,
    },
    {
      label: "Cash Snapshot",
      timestamp: data.cash_snapshot_time,
      sourceType: data.cash_source_type,
      detail: data.cash_detail,
    },
    {
      label: "Price Snapshot",
      timestamp: data.price_snapshot_time,
      sourceType: data.price_source_type,
      detail: data.price_detail,
    },
    {
      label: "FX Snapshot",
      timestamp: data.fx_snapshot_time,
      sourceType: data.fx_source_type,
      detail: data.fx_detail,
    },
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
        Snapshot Metadata
      </div>

      <div style={{ padding: "10px 16px" }}>
        {rows.map((row) => (
          <div
            key={row.label}
            style={{
              display: "grid",
              gap: "6px",
              padding: "12px 0",
              borderBottom: "1px solid #f3f4f6",
            }}
          >
            <div style={{ fontSize: "14px", fontWeight: 600 }}>{row.label}</div>

            <div style={{ color: "#6b7280", fontSize: "13px" }}>
              Time: {formatTimestamp(row.timestamp)}
            </div>

            <div style={{ color: "#6b7280", fontSize: "13px" }}>
              Source: {row.sourceType ?? "N/A"}
            </div>

            <div style={{ color: "#6b7280", fontSize: "13px" }}>
              Detail: {row.detail ?? "N/A"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}