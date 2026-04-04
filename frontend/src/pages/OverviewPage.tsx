import { useQuery } from "@tanstack/react-query";

import { fetchConcentration, fetchOverviewSummary, fetchTopHoldings } from "../api/overview";
import { SummaryCard } from "../components/cards/SummaryCard";
import { ConcentrationPanel } from "../components/panels/ConcentrationPanel";
import { TopHoldingsTable } from "../components/tables/TopHoldingsTable";
import { formatCurrency, formatPercent, formatTimestamp } from "../utils/format";

export function OverviewPage() {
  const overviewQuery = useQuery({
    queryKey: ["overview"],
    queryFn: fetchOverviewSummary,
  });

  const topHoldingsQuery = useQuery({
    queryKey: ["overview", "top-holdings"],
    queryFn: fetchTopHoldings,
  });

  const concentrationQuery = useQuery({
    queryKey: ["overview", "concentration"],
    queryFn: fetchConcentration,
  });

  if (overviewQuery.isLoading || topHoldingsQuery.isLoading || concentrationQuery.isLoading) {
    return <div>Loading dashboard...</div>;
  }

  if (overviewQuery.isError || topHoldingsQuery.isError || concentrationQuery.isError) {
    return (
      <div>
        <h1 style={{ marginBottom: "12px" }}>Overview</h1>
        <div style={{ color: "crimson" }}>
          Failed to load dashboard data. Check backend/CORS/API status.
        </div>
      </div>
    );
  }

  const overview = overviewQuery.data!.data;
  const topHoldings = topHoldingsQuery.data!.data;
  const concentration = concentrationQuery.data!.data;
  const snapshotTime = overviewQuery.data!.meta.snapshot_time;

  return (
    <div style={{ display: "grid", gap: "24px" }}>
      <div>
        <h1 style={{ fontSize: "28px", margin: 0 }}>Overview</h1>
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
        <SummaryCard
          label="Total NAV"
          value={formatCurrency(overview.total_nav_base)}
          subValue="Base currency: USD"
        />
        <SummaryCard
          label="Total Equity"
          value={formatCurrency(overview.total_equity_value_base)}
        />
        <SummaryCard
          label="Total Cash"
          value={formatCurrency(overview.total_cash_base)}
        />
        <SummaryCard
          label="Unrealized P&L"
          value={formatCurrency(overview.total_unrealized_pnl_base)}
          subValue={formatPercent(overview.total_unrealized_return_pct)}
        />

        <SummaryCard
          label="KR Equity Value"
          value={formatCurrency(overview.kr_equity_value_base)}
        />
        <SummaryCard
          label="US Equity Value"
          value={formatCurrency(overview.us_equity_value_base)}
        />
        <SummaryCard
          label="KRW Cash (USD base)"
          value={formatCurrency(overview.krw_cash_base)}
        />
        <SummaryCard
          label="USD Cash"
          value={formatCurrency(overview.usd_cash_base)}
        />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "16px",
          alignItems: "start",
        }}
      >
        <TopHoldingsTable rows={topHoldings} />
        <ConcentrationPanel data={concentration} />
      </div>
    </div>
  );
}