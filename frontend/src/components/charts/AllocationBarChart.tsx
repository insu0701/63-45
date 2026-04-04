import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Row = {
  label: string;
  value: number;
};

type Props = {
  title: string;
  rows: Row[];
};

export function AllocationBarChart({ title, rows }: Props) {
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

      <div style={{ width: "100%", height: 320, padding: "12px 16px 16px" }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows} margin={{ top: 8, right: 8, left: 8, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}