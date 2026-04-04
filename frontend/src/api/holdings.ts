import { apiClient } from "./client";
import type { ApiResponse } from "../types/api";
import type {
  HoldingDetailItem,
  HoldingListItem,
  HoldingsFilterState,
} from "../types/holdings";

export async function fetchHoldings(
  filters: HoldingsFilterState
): Promise<ApiResponse<HoldingListItem[]>> {
  const params: Record<string, string | number | boolean> = {};

  if (filters.sleeve !== "ALL") {
    params.sleeve = filters.sleeve;
  }

  if (filters.sector.trim()) {
    params.sector = filters.sector.trim();
  }

  if (filters.search.trim()) {
    params.search = filters.search.trim();
  }

  if (filters.performance === "WINNERS") {
    params.winners_only = true;
  }

  if (filters.performance === "LOSERS") {
    params.losers_only = true;
  }

  if (filters.minWeightPercent.trim()) {
    const value = Number(filters.minWeightPercent);
    if (!Number.isNaN(value) && value > 0) {
      params.min_weight = value / 100;
    }
  }

  const response = await apiClient.get<ApiResponse<HoldingListItem[]>>(
    "/api/v1/holdings",
    { params }
  );

  return response.data;
}

export async function fetchHoldingDetail(
  symbol: string
): Promise<ApiResponse<HoldingDetailItem>> {
  const response = await apiClient.get<ApiResponse<HoldingDetailItem>>(
    `/api/v1/holdings/${symbol}`
  );
  return response.data;
}