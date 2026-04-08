import { useQuery } from "@tanstack/react-query";

import { fetchDecisionLog, fetchStrategyOverlay } from "../api/strategy";
import { SummaryCard } from "../components/cards/SummaryCard";
import { DailyDecisionLogTable } from "../components/tables/DailyDecisionLogTable";
import { StrategyOverlayTable } from "../components/tables/StrategyOverlayTable";

export function StrategyPage() {
  const overlayQuery = useQuery({
    queryKey: ["strategy-overlay"],
    queryFn: () => fetchStrategyOverlay(),
  });

  const decisionLogQuery = useQuery({
    queryKey: ["strategy-decision-log"],
    queryFn: () => fetchDecisionLog(50),
  });

  if (overlayQuery.isLoading || decisionLogQuery.isLoading) {
    return <div>Loading strategy data...</div>;
  }

  if (overlayQuery.isError || decisionLogQuery.isError) {
    return (
      <div>
        <h1 style={{ marginBottom: "12px" }}>Strategy</h1>
        <div style={{ color: "crimson" }}>
          Failed to load strategy overlay or decision log data.
        </div>
      </div>
    );
  }

  const overlayRows = overlayQuery.data?.data ?? [];
  const decisionRows = decisionLogQuery.data?.data ?? [];

  const rowsWithTarget = overlayRows.filter((row) => row.target_state !== null).length;
  const rowsWithDelta = overlayRows.filter((row) => row.actual_vs_target_delta !== null).length;

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "28px", margin: 0 }}>Strategy</h1>
        <p style={{ color: "#6b7280", marginTop: "8px" }}>
          Placeholder strategy-state hooks and daily decision log scaffolding.
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
          gap: "16px",
        }}
      >
        <SummaryCard label="Overlay Rows" value={String(overlayRows.length)} />
        <SummaryCard label="Decision Logs" value={String(decisionRows.length)} />
        <SummaryCard label="Rows With Target" value={String(rowsWithTarget)} />
        <SummaryCard label="Rows With Delta" value={String(rowsWithDelta)} />
      </div>

      <StrategyOverlayTable rows={overlayRows} />
      <DailyDecisionLogTable rows={decisionRows} />
    </div>
  );
}