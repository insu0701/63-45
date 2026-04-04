import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
};

export function AppShell({ children }: Props) {
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#f3f4f6",
        color: "#111827",
      }}
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "220px 1fr",
          minHeight: "100vh",
        }}
      >
        <aside
          style={{
            background: "#111827",
            color: "white",
            padding: "24px 16px",
          }}
        >
          <div style={{ fontSize: "20px", fontWeight: 700, marginBottom: "24px" }}>63-45</div>
          <div style={{ display: "grid", gap: "10px" }}>
            <div style={navItemActive}>Overview</div>
            <div style={navItemDisabled}>Holdings</div>
            <div style={navItemDisabled}>Allocation</div>
            <div style={navItemDisabled}>Sync / Health</div>
          </div>
        </aside>

        <main style={{ padding: "24px 28px" }}>{children}</main>
      </div>
    </div>
  );
}

const navItemActive: React.CSSProperties = {
  padding: "10px 12px",
  borderRadius: "8px",
  background: "#1f2937",
  fontWeight: 600,
};

const navItemDisabled: React.CSSProperties = {
  padding: "10px 12px",
  borderRadius: "8px",
  color: "#9ca3af",
};