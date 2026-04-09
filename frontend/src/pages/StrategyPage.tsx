import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchDecisionLog,
  fetchStrategyOptions,
  fetchStrategyOverlay,
  saveManualStrategyOverlay,
} from "../api/strategy";
import { SummaryCard } from "../components/cards/SummaryCard";
import { StrategyOverlayEditor } from "../components/forms/StrategyOverlayEditor";
import { DailyDecisionLogTable } from "../components/tables/DailyDecisionLogTable";
import { StrategyOverlayTable } from "../components/tables/StrategyOverlayTable";

export function StrategyPage() {
  const queryClient = useQueryClient();
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState("");

  const overlayQuery = useQuery({
    queryKey: ["strategy-overlay"],
    queryFn: () => fetchStrategyOverlay(),
  });

  const decisionLogQuery = useQuery({
    queryKey: ["strategy-decision-log"],
    queryFn: () => fetchDecisionLog(50),
  });

  const optionsQuery = useQuery({
    queryKey: ["strategy-options"],
    queryFn: () => fetchStrategyOptions(),
  });

  const saveMutation = useMutation({
    mutationFn: saveManualStrategyOverlay,
    onSuccess: (result) => {
      setActionMessage(
        `Manual overlay saved for ${result.data.symbol}. Decision log written: ${
          result.data.decision_log_written ? "yes" : "no"
        }.`
      );
      queryClient.invalidateQueries({ queryKey: ["strategy-overlay"] });
      queryClient.invalidateQueries({ queryKey: ["strategy-decision-log"] });
    },
    onError: () => {
      setActionMessage("Manual overlay save failed.");
    },
  });

  const overlayRows = overlayQuery.data?.data ?? [];
  const decisionRows = decisionLogQuery.data?.data ?? [];
  const options = optionsQuery.data?.data ?? null;

  useEffect(() => {
    if (overlayRows.length === 0) {
      setSelectedKey(null);
      return;
    }

    const existing = overlayRows.find(
      (row) => `${row.symbol}::${row.sleeve}` === selectedKey
    );

    if (!existing) {
      setSelectedKey(`${overlayRows[0].symbol}::${overlayRows[0].sleeve}`);
    }
  }, [overlayRows, selectedKey]);

  const selectedRow = useMemo(() => {
    if (!selectedKey) return null;

    return (
      overlayRows.find((row) => `${row.symbol}::${row.sleeve}` === selectedKey) ?? null
    );
  }, [overlayRows, selectedKey]);

  const rowsWithTarget = overlayRows.filter((row) => row.target_state !== null).length;
  const rowsWithDelta = overlayRows.filter((row) => row.actual_vs_target_delta !== null).length;

  const isLoading =
    overlayQuery.isLoading || decisionLogQuery.isLoading || optionsQuery.isLoading;

  const isError =
    overlayQuery.isError || decisionLogQuery.isError || optionsQuery.isError;

  if (isLoading) {
    return <div>Loading strategy data...</div>;
  }

  if (isError) {
    return (
      <div>
        <h1 style={{ marginBottom: "12px" }}>Strategy</h1>
        <div style={{ color: "crimson" }}>
          Failed to load strategy overlay, options, or decision-log data.
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "28px", margin: 0 }}>Strategy</h1>
        <p style={{ color: "#6b7280", marginTop: "8px" }}>
          Manual strategy overlay input and reason-coded daily decision-log flow.
        </p>
      </div>

      {actionMessage ? (
        <div
          style={{
            padding: "12px 16px",
            borderRadius: "10px",
            background: "#eff6ff",
            border: "1px solid #bfdbfe",
            color: "#1d4ed8",
          }}
        >
          {actionMessage}
        </div>
      ) : null}

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

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "minmax(0, 2fr) minmax(360px, 1fr)",
          gap: "16px",
          alignItems: "start",
        }}
      >
        <StrategyOverlayTable
          rows={overlayRows}
          selectedKey={selectedKey}
          onSelect={(row) => setSelectedKey(`${row.symbol}::${row.sleeve}`)}
        />

        <StrategyOverlayEditor
          selectedRow={selectedRow}
          options={options}
          isSaving={saveMutation.isPending}
          onSave={(payload) => saveMutation.mutate(payload)}
        />
      </div>

      <DailyDecisionLogTable rows={decisionRows} />
    </div>
  );
}