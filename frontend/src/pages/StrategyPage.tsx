import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchDecisionLog,
  fetchStrategyOptions,
  fetchStrategyOverlay,
  fetchStrategyReview,
  saveManualStrategyOverlay,
} from "../api/strategy";
import { SummaryCard } from "../components/cards/SummaryCard";
import { StrategyOverlayEditor } from "../components/forms/StrategyOverlayEditor";
import { DailyDecisionLogTable } from "../components/tables/DailyDecisionLogTable";
import { RebalanceCandidatesTable } from "../components/tables/RebalanceCandidatesTable";
import { StrategyOverlayTable } from "../components/tables/StrategyOverlayTable";
import { formatCurrency } from "../utils/format";

export function StrategyPage() {
  const queryClient = useQueryClient();
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState("");
  const [minAbsDelta, setMinAbsDelta] = useState("1000");

  const overlayQuery = useQuery({
    queryKey: ["strategy-overlay"],
    queryFn: () => fetchStrategyOverlay(),
  });

  const reviewQuery = useQuery({
    queryKey: ["strategy-review", minAbsDelta],
    queryFn: () => fetchStrategyReview(Number(minAbsDelta || "0"), 25),
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
      queryClient.invalidateQueries({ queryKey: ["strategy-review"] });
      queryClient.invalidateQueries({ queryKey: ["strategy-decision-log"] });
    },
    onError: () => {
      setActionMessage("Manual overlay save failed.");
    },
  });

  const overlayRows = overlayQuery.data?.data ?? [];
  const reviewPayload = reviewQuery.data?.data ?? null;
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

  const isLoading =
    overlayQuery.isLoading ||
    reviewQuery.isLoading ||
    decisionLogQuery.isLoading ||
    optionsQuery.isLoading;

  const isError =
    overlayQuery.isError ||
    reviewQuery.isError ||
    decisionLogQuery.isError ||
    optionsQuery.isError;

  if (isLoading) {
    return <div>Loading strategy data...</div>;
  }

  if (isError) {
    return (
      <div>
        <h1 style={{ marginBottom: "12px" }}>Strategy</h1>
        <div style={{ color: "crimson" }}>
          Failed to load strategy overlay, review data, options, or decision-log data.
        </div>
      </div>
    );
  }

  const reviewMetrics = reviewPayload?.metrics ?? {
    overlay_row_count: 0,
    rows_with_target: 0,
    rows_without_target: 0,
    rows_with_delta: 0,
    on_target_count: 0,
    add_count: 0,
    trim_count: 0,
    exit_count: 0,
    gross_abs_delta_dollars: 0,
    net_delta_dollars: 0,
  };

  const candidateRows = reviewPayload?.candidates ?? [];

  const rowsWithTarget = overlayRows.filter((row) => row.target_state !== null).length;
  const rowsWithDelta = overlayRows.filter((row) => row.actual_vs_target_delta !== null).length;

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "28px", margin: 0 }}>Strategy</h1>
        <p style={{ color: "#6b7280", marginTop: "8px" }}>
          Manual strategy overlay input, target-vs-actual review, and reason-coded decision-log flow.
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
          gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
          gap: "16px",
        }}
      >
        <SummaryCard label="Add Candidates" value={String(reviewMetrics.add_count)} />
        <SummaryCard label="Trim Candidates" value={String(reviewMetrics.trim_count)} />
        <SummaryCard label="Exit Candidates" value={String(reviewMetrics.exit_count)} />
        <SummaryCard
          label="Gross Abs Delta"
          value={formatCurrency(reviewMetrics.gross_abs_delta_dollars, "USD", 0)}
        />
      </div>

      <div
        style={{
          border: "1px solid #e5e7eb",
          borderRadius: "12px",
          background: "white",
          padding: "16px",
          display: "grid",
          gridTemplateColumns: "220px 220px 1fr",
          gap: "12px",
          alignItems: "end",
        }}
      >
        <label style={{ display: "grid", gap: "6px" }}>
          <span style={{ fontSize: "13px", color: "#6b7280" }}>Candidate Threshold ($)</span>
          <input
            value={minAbsDelta}
            onChange={(e) => setMinAbsDelta(e.target.value)}
            style={inputStyle}
          />
        </label>

        <button
          onClick={() =>
            queryClient.invalidateQueries({ queryKey: ["strategy-review"] })
          }
          style={buttonStyle}
        >
          Refresh Review Panel
        </button>

        <div style={{ fontSize: "13px", color: "#6b7280" }}>
          Net delta: {formatCurrency(reviewMetrics.net_delta_dollars, "USD", 0)} ·
          On target: {reviewMetrics.on_target_count} ·
          Without target: {reviewMetrics.rows_without_target}
        </div>
      </div>

      <RebalanceCandidatesTable
        rows={candidateRows}
        selectedKey={selectedKey}
        onSelect={(row) => setSelectedKey(`${row.symbol}::${row.sleeve}`)}
      />

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

const inputStyle: React.CSSProperties = {
  height: "40px",
  borderRadius: "8px",
  border: "1px solid #d1d5db",
  padding: "0 12px",
  fontSize: "14px",
  background: "white",
  width: "100%",
};

const buttonStyle: React.CSSProperties = {
  height: "40px",
  padding: "0 16px",
  borderRadius: "8px",
  border: "1px solid #d1d5db",
  background: "white",
  cursor: "pointer",
  fontWeight: 600,
};