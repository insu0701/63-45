import { apiClient } from "./client";
import type { ApiResponse } from "../types/api";
import type { DailyDecisionLogItem, StrategyOverlayItem } from "../types/strategy";

export async function fetchStrategyOverlay(sleeve?: string) {
  const params = sleeve ? { sleeve } : {};
  const response = await apiClient.get<ApiResponse<StrategyOverlayItem[]>>(
    "/api/v1/strategy/overlay",
    { params }
  );
  return response.data;
}

export async function fetchDecisionLog(limit = 50, sleeve?: string) {
  const params = sleeve ? { limit, sleeve } : { limit };
  const response = await apiClient.get<ApiResponse<DailyDecisionLogItem[]>>(
    "/api/v1/strategy/decision-log",
    { params }
  );
  return response.data;
}