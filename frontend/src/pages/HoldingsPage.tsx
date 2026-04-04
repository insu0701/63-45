import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { fetchHoldingDetail, fetchHoldings } from "../api/holdings";
import { HoldingsFilters } from "../components/filters/HoldingsFilters";
import { HoldingDetailDrawer } from "../components/panels/HoldingDetailDrawer";
import { HoldingsTable } from "../components/tables/HoldingsTable";
import type { HoldingsFilterState } from "../types/holdings";
import { formatTimestamp } from "../utils/format";

const initialFilters: HoldingsFilterState = {
  sleeve: "ALL",
  sector: "",
  search: "",
  performance: "ALL",
  minWeightPercent: "",
};

export function HoldingsPage() {
  const [filters, setFilters] = useState<HoldingsFilterState>(initialFilters);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);

  const holdingsQuery = useQuery({
    queryKey: ["holdings", filters],
    queryFn: () => fetchHoldings(filters),
  });

  const detailQuery = useQuery({
    queryKey: ["holding-detail", selectedSymbol],
    queryFn: () => fetchHoldingDetail(selectedSymbol!),
    enabled: !!selectedSymbol,
  });

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "28px", margin: 0 }}>Holdings</h1>
        <p style={{ color: "#6b7280", marginTop: "8px" }}>
          Snapshot time: {formatTimestamp(holdingsQuery.data?.meta.snapshot_time ?? null)}
        </p>
      </div>

      <HoldingsFilters
        filters={filters}
        onChange={(patch) => setFilters((prev) => ({ ...prev, ...patch }))}
        onReset={() => setFilters(initialFilters)}
      />

      {holdingsQuery.isLoading ? (
        <div>Loading holdings...</div>
      ) : holdingsQuery.isError ? (
        <div style={{ color: "crimson" }}>
          Failed to load holdings. Check backend/API state.
        </div>
      ) : (
        <HoldingsTable
          rows={holdingsQuery.data?.data ?? []}
          selectedSymbol={selectedSymbol}
          onSelect={setSelectedSymbol}
        />
      )}

      <HoldingDetailDrawer
        isOpen={!!selectedSymbol}
        isLoading={detailQuery.isLoading}
        data={detailQuery.data?.data ?? null}
        onClose={() => setSelectedSymbol(null)}
      />
    </div>
  );
}