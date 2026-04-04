import { useQuery } from "@tanstack/react-query";

import {
  fetchCountryAllocation,
  fetchCurrencyAllocation,
  fetchSectorAllocation,
  fetchSleeveAllocation,
} from "../api/allocation";
import { AllocationBarChart } from "../components/charts/AllocationBarChart";
import { AllocationTable } from "../components/tables/AllocationTable";
import { formatTimestamp } from "../utils/format";

export function AllocationPage() {
  const sleeveQuery = useQuery({
    queryKey: ["allocation", "sleeve"],
    queryFn: fetchSleeveAllocation,
  });

  const countryQuery = useQuery({
    queryKey: ["allocation", "country"],
    queryFn: fetchCountryAllocation,
  });

  const sectorQuery = useQuery({
    queryKey: ["allocation", "sector"],
    queryFn: fetchSectorAllocation,
  });

  const currencyQuery = useQuery({
    queryKey: ["allocation", "currency"],
    queryFn: fetchCurrencyAllocation,
  });

  const isLoading =
    sleeveQuery.isLoading ||
    countryQuery.isLoading ||
    sectorQuery.isLoading ||
    currencyQuery.isLoading;

  const isError =
    sleeveQuery.isError ||
    countryQuery.isError ||
    sectorQuery.isError ||
    currencyQuery.isError;

  if (isLoading) {
    return <div>Loading allocation...</div>;
  }

  if (isError) {
    return (
      <div>
        <h1 style={{ marginBottom: "12px" }}>Allocation</h1>
        <div style={{ color: "crimson" }}>
          Failed to load allocation data. Check backend/API state.
        </div>
      </div>
    );
  }

  const sleeveRows = sleeveQuery.data?.data ?? [];
  const countryRows = countryQuery.data?.data ?? [];
  const sectorRows = sectorQuery.data?.data ?? [];
  const currencyRows = currencyQuery.data?.data ?? [];

  const snapshotTime =
    sleeveQuery.data?.meta.snapshot_time ??
    countryQuery.data?.meta.snapshot_time ??
    sectorQuery.data?.meta.snapshot_time ??
    currencyQuery.data?.meta.snapshot_time ??
    null;

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "28px", margin: 0 }}>Allocation</h1>
        <p style={{ color: "#6b7280", marginTop: "8px" }}>
          Snapshot time: {formatTimestamp(snapshotTime)}
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "16px",
          alignItems: "start",
        }}
      >
        <AllocationBarChart
          title="Sleeve Allocation"
          rows={sleeveRows.map((row) => ({
            label: row.sleeve,
            value: row.market_value_base,
          }))}
        />
        <AllocationTable
          title="Sleeve Allocation Table"
          rows={sleeveRows.map((row) => ({
            label: row.sleeve,
            marketValueBase: row.market_value_base,
            weightOfTotalNav: row.weight_of_total_nav,
            extra: `${row.position_count} positions`,
          }))}
        />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "16px",
          alignItems: "start",
        }}
      >
        <AllocationBarChart
          title="Country Allocation"
          rows={countryRows.map((row) => ({
            label: row.country,
            value: row.market_value_base,
          }))}
        />
        <AllocationTable
          title="Country Allocation Table"
          rows={countryRows.map((row) => ({
            label: row.country,
            marketValueBase: row.market_value_base,
            weightOfTotalNav: row.weight_of_total_nav,
          }))}
        />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "16px",
          alignItems: "start",
        }}
      >
        <AllocationBarChart
          title="Sector Allocation"
          rows={sectorRows.map((row) => ({
            label: row.sector,
            value: row.market_value_base,
          }))}
        />
        <AllocationTable
          title="Sector Allocation Table"
          rows={sectorRows.map((row) => ({
            label: row.sector,
            marketValueBase: row.market_value_base,
            weightOfTotalNav: row.weight_of_total_nav,
          }))}
        />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "16px",
          alignItems: "start",
        }}
      >
        <AllocationBarChart
          title="Currency Allocation"
          rows={currencyRows.map((row) => ({
            label: row.currency,
            value: row.total_base_value,
          }))}
        />
        <AllocationTable
          title="Currency Allocation Table"
          rows={currencyRows.map((row) => ({
            label: row.currency,
            totalBaseValue: row.total_base_value,
            weightOfTotalNav: row.weight_of_total_nav,
          }))}
          valueLabel="USD Base Value"
        />
      </div>
    </div>
  );
}