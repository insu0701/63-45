import type { OverviewCashCurrency } from "../../types/overview";
import { formatCurrency, formatTimestamp } from "../../utils/format";

type Props = {
  data: OverviewCashCurrency;
};

function formatFxRate(value: number | null | undefined, fractionDigits: number) {
  if (value == null) return "N/A";
  return value.toLocaleString(undefined, {
    minimumFractionDigits: fractionDigits,
    maximumFractionDigits: fractionDigits,
  });
}

export function CashCurrencyPanel({ data }: Props) {
  const base = data.base_currency;

  const rows = [
    {
      label: "KRW Cash (native)",
      value: formatCurrency(data.krw_cash_native, "KRW", 0),
    },
    {
      label: `KRW Cash (${base} base)`,
      value: formatCurrency(data.krw_cash_base, base, 0),
    },
    {
      label: "USD Cash (native)",
      value: formatCurrency(data.usd_cash_native, "USD", 2),
    },
    {
      label: `USD Cash (${base} base)`,
      value: formatCurrency(data.usd_cash_base, base, 0),
    },
    {
      label: `Total Cash (${base} base)`,
      value: formatCurrency(data.total_cash_base, base, 0),
    },
    {
      label: `KRW → ${base} FX`,
      value: formatFxRate(data.fx_rate_krw_to_base, 6),
    },
    {
      label: `${base} → KRW FX`,
      value: formatFxRate(data.fx_rate_base_to_krw, 2),
    },
    {
      label: "FX Timestamp",
      value: formatTimestamp(data.fx_rate_timestamp),
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
        Cash / FX
      </div>

      <div style={{ padding: "10px 16px" }}>
        {rows.map((row) => (
          <div
            key={row.label}
            style={{
              display: "grid",
              gridTemplateColumns: "1fr auto",
              gap: "12px",
              padding: "10px 0",
              borderBottom: "1px solid #f3f4f6",
            }}
          >
            <div style={{ color: "#6b7280", fontSize: "14px" }}>{row.label}</div>
            <div style={{ fontSize: "14px", fontWeight: 600 }}>{row.value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}