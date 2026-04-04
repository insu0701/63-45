import type { ReactNode } from "react";

export type PageKey = "overview" | "holdings" | "allocation";

type Props = {
  currentPage: PageKey;
  onNavigate: (page: PageKey) => void;
  children: ReactNode;
};

export function AppShell({ currentPage, onNavigate, children }: Props) {
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
            <button
              onClick={() => onNavigate("overview")}
              style={currentPage === "overview" ? navItemActive : navItem}
            >
              Overview
            </button>

            <button
              onClick={() => onNavigate("holdings")}
              style={currentPage === "holdings" ? navItemActive : navItem}
            >
              Holdings
            </button>

            <button
              onClick={() => onNavigate("allocation")}
              style={currentPage === "allocation" ? navItemActive : navItem}
            >
              Allocation
            </button>

            <div style={navItemDisabled}>Sync / Health</div>
          </div>
        </aside>

        <main style={{ padding: "24px 28px" }}>{children}</main>
      </div>
    </div>
  );
}

const navItem: React.CSSProperties = {
  padding: "10px 12px",
  borderRadius: "8px",
  background: "transparent",
  color: "white",
  border: "1px solid transparent",
  textAlign: "left",
  cursor: "pointer",
};

const navItemActive: React.CSSProperties = {
  padding: "10px 12px",
  borderRadius: "8px",
  background: "#1f2937",
  color: "white",
  border: "1px solid transparent",
  textAlign: "left",
  cursor: "pointer",
  fontWeight: 600,
};

const navItemDisabled: React.CSSProperties = {
  padding: "10px 12px",
  borderRadius: "8px",
  color: "#9ca3af",
};