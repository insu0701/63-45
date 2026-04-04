import type { HoldingDetailItem } from "../../types/holdings";
import { formatCurrency, formatPercent, formatTimestamp } from "../../utils/format";

type Props = {
  isOpen: boolean;
  isLoading: boolean;
  data: HoldingDetailItem | null;
  onClose: () => void;
};

export function HoldingDetailDrawer({ isOpen, isLoading, data, onClose }: Props) {
  if (!isOpen) return null;

  return (
    <>
      <div
        onClick={onClose}
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(0,0,0,0.2)",
        }}
      />

      <aside
        style={{
          position: "fixed",
          top: 0,
          right: 0,
          width: "420px",
          height: "100vh",
          background: "white",
          boxShadow: "-8px 0 24px rgba(0,0,0,0.12)",
          padding: "24px",
          overflowY: "auto",
          zIndex: 10,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "22px" }}>Holding Detail</h2>
            <div style={{ color: "#6b7280", marginTop: "6px" }}>
              {data ? `${data.symbol} · ${data.security_name}` : "Loading..."}
            </div>
          </div>

          <button
            onClick={onClose}
            style={{
              border: "1px solid #d1d5db",
              background: "white",
              borderRadius: "8px",
              padding: "8px 12px",
              cursor: "pointer",
            }}
          >
            Close
          </button>
        </div>

        {isLoading ? (
          <div>Loading detail...</div>
        ) : !data ? (
          <div>No data.</div>
        ) : (
          <div style={{ display: "grid", gap: "12px" }}>
            <DetailRow label="Sleeve" value={data.sleeve} />
            <DetailRow label="Country" value={data.country} />
            <DetailRow label="Market" value={data.market} />
            <DetailRow label="Currency" value={data.currency} />
            <DetailRow label="Sector" value={data.sector ?? "Unknown"} />
            <DetailRow label="Industry" value={data.industry ?? "Unknown"} />
            <DetailRow label="Quantity" value={String(data.quantity)} />
            <DetailRow
              label="Average Cost (native)"
              value={data.avg_cost_native != null ? formatCurrency(data.avg_cost_native, data.currency) : "N/A"}
            />
            <DetailRow
              label="Current Price (native)"
              value={data.current_price_native != null ? formatCurrency(data.current_price_native, data.currency) : "N/A"}
            />
            <DetailRow
              label="Cost Basis (native)"
              value={data.cost_basis_native != null ? formatCurrency(data.cost_basis_native, data.currency) : "N/A"}
            />
            <DetailRow
              label="Market Value (native)"
              value={data.market_value_native != null ? formatCurrency(data.market_value_native, data.currency) : "N/A"}
            />
            <DetailRow
              label="Unrealized P&L (native)"
              value={data.unrealized_pnl_native != null ? formatCurrency(data.unrealized_pnl_native, data.currency) : "N/A"}
            />
            <DetailRow
              label="Unrealized Return"
              value={data.unrealized_return_pct != null ? formatPercent(data.unrealized_return_pct) : "N/A"}
            />
            <DetailRow
              label="FX Rate to Base"
              value={data.fx_rate_to_base != null ? String(data.fx_rate_to_base) : "N/A"}
            />
            <DetailRow
              label="Cost Basis (USD)"
              value={data.cost_basis_base != null ? formatCurrency(data.cost_basis_base) : "N/A"}
            />
            <DetailRow
              label="Market Value (USD)"
              value={data.market_value_base != null ? formatCurrency(data.market_value_base) : "N/A"}
            />
            <DetailRow
              label="Unrealized P&L (USD)"
              value={data.unrealized_pnl_base != null ? formatCurrency(data.unrealized_pnl_base) : "N/A"}
            />
            <DetailRow label="Price Timestamp" value={formatTimestamp(data.price_timestamp)} />
            <DetailRow label="Snapshot Time" value={formatTimestamp(data.snapshot_time)} />
            <DetailRow label="Source Type" value={data.source_type} />
          </div>
        )}
      </aside>
    </>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        gap: "12px",
        paddingBottom: "10px",
        borderBottom: "1px solid #f3f4f6",
      }}
    >
      <span style={{ color: "#6b7280" }}>{label}</span>
      <strong style={{ textAlign: "right" }}>{value}</strong>
    </div>
  );
}