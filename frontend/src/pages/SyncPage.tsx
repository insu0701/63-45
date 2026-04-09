import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  importUsHoldingsCsv,
  runFullSync,
  runFxSync,
  runKiwoomSync,
  runPriceSync,
} from "../api/imports";
import { fetchSyncStatus } from "../api/sync";
import { SummaryCard } from "../components/cards/SummaryCard";
import { SourceStatusGrid } from "../components/cards/SourceStatusGrid";
import { SyncActionsPanel } from "../components/panels/SyncActionsPanel";
import { DataIssuesTable } from "../components/tables/DataIssuesTable";
import { SyncRunsTable } from "../components/tables/SyncRunsTable";
import { formatTimestamp } from "../utils/format";

function invalidatePortfolioQueries(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: ["sync-status"] });
  queryClient.invalidateQueries({ queryKey: ["overview"] });
  queryClient.invalidateQueries({ queryKey: ["overview", "top-holdings"] });
  queryClient.invalidateQueries({ queryKey: ["overview", "concentration"] });
  queryClient.invalidateQueries({ queryKey: ["holdings"] });
  queryClient.invalidateQueries({ queryKey: ["allocation"] });
  queryClient.invalidateQueries({ queryKey: ["strategy-overlay"] });
  queryClient.invalidateQueries({ queryKey: ["strategy-review"] });
  queryClient.invalidateQueries({ queryKey: ["strategy-decision-log"] });
}

export function SyncPage() {
  const queryClient = useQueryClient();
  const [actionMessage, setActionMessage] = useState("");

  const query = useQuery({
    queryKey: ["sync-status"],
    queryFn: fetchSyncStatus,
  });

  const fullSyncMutation = useMutation({
    mutationFn: runFullSync,
    onSuccess: (result) => {
      setActionMessage(
        `Full refresh complete. FX rates: ${result.data.fx_rates_written}, Kiwoom holdings: ${result.data.holdings_written}, repriced holdings: ${result.data.price_refresh_holdings_written}, price rows: ${result.data.price_refresh_prices_written}.`
      );
      invalidatePortfolioQueries(queryClient);
    },
    onError: () => {
      setActionMessage("Full refresh failed.");
    },
  });

  const kiwoomSyncMutation = useMutation({
    mutationFn: runKiwoomSync,
    onSuccess: (result) => {
      setActionMessage(
        `Kiwoom sync complete. Holdings written: ${result.data.holdings_written}, cash rows: ${result.data.cash_rows_written}.`
      );
      invalidatePortfolioQueries(queryClient);
    },
    onError: () => {
      setActionMessage("Kiwoom sync failed.");
    },
  });

  const priceSyncMutation = useMutation({
    mutationFn: runPriceSync,
    onSuccess: (result) => {
      setActionMessage(
        `Price refresh complete. Repriced holdings: ${result.data.holdings_written}, price rows: ${result.data.prices_written}, carry-forward symbols: ${result.data.carry_forward_symbols}.`
      );
      invalidatePortfolioQueries(queryClient);
    },
    onError: () => {
      setActionMessage("Price refresh failed.");
    },
  });

  const fxSyncMutation = useMutation({
    mutationFn: runFxSync,
    onSuccess: (result) => {
      setActionMessage(
        `FX sync complete. Rates written: ${result.data.rates_written}. Provider: ${result.data.provider}.`
      );
      queryClient.invalidateQueries({ queryKey: ["sync-status"] });
    },
    onError: () => {
      setActionMessage("FX sync failed.");
    },
  });

  const usImportMutation = useMutation({
    mutationFn: ({ file, usdCash }: { file: File; usdCash: string }) =>
      importUsHoldingsCsv(file, usdCash),
    onSuccess: (result) => {
      setActionMessage(
        `US import complete. Holdings written: ${result.data.holdings_written}, imported symbols: ${(result.data.imported_symbols ?? []).join(", ")}`
      );
      invalidatePortfolioQueries(queryClient);
    },
    onError: () => {
      setActionMessage("US CSV import failed.");
    },
  });

  if (query.isLoading) {
    return <div>Loading sync / health data...</div>;
  }

  if (query.isError) {
    return (
      <div>
        <h1 style={{ marginBottom: "12px" }}>Sync / Health</h1>
        <div style={{ color: "crimson" }}>
          Failed to load sync / health data. Check backend/API state.
        </div>
      </div>
    );
  }

  const payload = query.data!.data;
  const snapshotTime = query.data!.meta.snapshot_time;

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "28px", margin: 0 }}>Sync / Health</h1>
        <p style={{ color: "#6b7280", marginTop: "8px" }}>
          Snapshot time: {formatTimestamp(snapshotTime)}
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
          gap: "16px",
        }}
      >
        <SummaryCard label="Fresh Sources" value={String(payload.summary.fresh_source_count)} />
        <SummaryCard label="Stale Sources" value={String(payload.summary.stale_source_count)} />
        <SummaryCard label="Missing Sources" value={String(payload.summary.missing_source_count)} />
        <SummaryCard label="Open Issues" value={String(payload.summary.open_issue_count)} />
      </div>

      <div>
        <button
          onClick={() => query.refetch()}
          style={{
            height: "40px",
            padding: "0 16px",
            borderRadius: "8px",
            border: "1px solid #d1d5db",
            background: "white",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          Refresh Page Data
        </button>
      </div>

      <SyncActionsPanel
        onRunFullSync={() => fullSyncMutation.mutate()}
        onRunKiwoomSync={() => kiwoomSyncMutation.mutate()}
        onRunPriceSync={() => priceSyncMutation.mutate()}
        onRunFxSync={() => fxSyncMutation.mutate()}
        onImportUsCsv={(file, usdCash) => usImportMutation.mutate({ file, usdCash })}
        isRunningFullSync={fullSyncMutation.isPending}
        isRunningKiwoomSync={kiwoomSyncMutation.isPending}
        isRunningPriceSync={priceSyncMutation.isPending}
        isRunningFxSync={fxSyncMutation.isPending}
        isImportingUsCsv={usImportMutation.isPending}
      />

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

      <SourceStatusGrid rows={payload.sources} />
      <SyncRunsTable rows={payload.sync_runs} />
      <DataIssuesTable rows={payload.data_issues} />
    </div>
  );
}