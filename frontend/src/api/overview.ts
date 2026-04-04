import { apiClient } from "./client";
import type { ApiResponse } from "../types/api";
import type { Concentration, OverviewSummary, TopHolding } from "../types/overview";

export async function fetchOverviewSummary(): Promise<ApiResponse<OverviewSummary>> {
  const response = await apiClient.get<ApiResponse<OverviewSummary>>("/api/v1/overview");
  return response.data;
}

export async function fetchTopHoldings(): Promise<ApiResponse<TopHolding[]>> {
  const response = await apiClient.get<ApiResponse<TopHolding[]>>("/api/v1/overview/top-holdings");
  return response.data;
}

export async function fetchConcentration(): Promise<ApiResponse<Concentration>> {
  const response = await apiClient.get<ApiResponse<Concentration>>("/api/v1/overview/concentration");
  return response.data;
}