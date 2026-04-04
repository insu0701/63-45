import type { HoldingsFilterState } from "../../types/holdings";

type Props = {
  filters: HoldingsFilterState;
  onChange: (patch: Partial<HoldingsFilterState>) => void;
  onReset: () => void;
};

export function HoldingsFilters({ filters, onChange, onReset }: Props) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(5, minmax(0, 1fr)) auto",
        gap: "12px",
        padding: "16px",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        background: "white",
      }}
    >
      <label style={fieldStyle}>
        <span style={labelStyle}>Sleeve</span>
        <select
          value={filters.sleeve}
          onChange={(e) =>
            onChange({ sleeve: e.target.value as HoldingsFilterState["sleeve"] })
          }
          style={inputStyle}
        >
          <option value="ALL">All</option>
          <option value="KR">KR</option>
          <option value="US">US</option>
        </select>
      </label>

      <label style={fieldStyle}>
        <span style={labelStyle}>Search</span>
        <input
          value={filters.search}
          onChange={(e) => onChange({ search: e.target.value })}
          placeholder="Symbol or name"
          style={inputStyle}
        />
      </label>

      <label style={fieldStyle}>
        <span style={labelStyle}>Sector</span>
        <input
          value={filters.sector}
          onChange={(e) => onChange({ sector: e.target.value })}
          placeholder="Exact sector match"
          style={inputStyle}
        />
      </label>

      <label style={fieldStyle}>
        <span style={labelStyle}>Performance</span>
        <select
          value={filters.performance}
          onChange={(e) =>
            onChange({
              performance: e.target.value as HoldingsFilterState["performance"],
            })
          }
          style={inputStyle}
        >
          <option value="ALL">All</option>
          <option value="WINNERS">Winners only</option>
          <option value="LOSERS">Losers only</option>
        </select>
      </label>

      <label style={fieldStyle}>
        <span style={labelStyle}>Min Weight (%)</span>
        <input
          value={filters.minWeightPercent}
          onChange={(e) => onChange({ minWeightPercent: e.target.value })}
          placeholder="e.g. 1"
          style={inputStyle}
        />
      </label>

      <div style={{ display: "flex", alignItems: "end" }}>
        <button
          onClick={onReset}
          style={{
            height: "40px",
            padding: "0 16px",
            borderRadius: "8px",
            border: "1px solid #d1d5db",
            background: "#f9fafb",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          Reset
        </button>
      </div>
    </div>
  );
}

const fieldStyle: React.CSSProperties = {
  display: "grid",
  gap: "6px",
};

const labelStyle: React.CSSProperties = {
  fontSize: "13px",
  color: "#6b7280",
};

const inputStyle: React.CSSProperties = {
  height: "40px",
  borderRadius: "8px",
  border: "1px solid #d1d5db",
  padding: "0 12px",
  fontSize: "14px",
  background: "white",
};