type SummaryCardProps = {
  label: string;
  value: string;
  subValue?: string;
};

export function SummaryCard({ label, value, subValue }: SummaryCardProps) {
  return (
    <div
      style={{
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        padding: "16px",
        background: "white",
        minHeight: "110px",
        boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
      }}
    >
      <div style={{ fontSize: "13px", color: "#6b7280", marginBottom: "8px" }}>{label}</div>
      <div style={{ fontSize: "26px", fontWeight: 700 }}>{value}</div>
      {subValue ? (
        <div style={{ fontSize: "13px", color: "#6b7280", marginTop: "8px" }}>{subValue}</div>
      ) : null}
    </div>
  );
}