import { apiClient } from "./client";
import type { ApiResponse } from "../types/api";
import type {
  DailyDecisionLogItem,
  ManualStrategyOverlayUpsertRequest,
  ManualStrategyOverlayUpsertResult,
  StrategyOptionsPayload,
  StrategyOverlayItem,
  StrategyReviewPayload,
} from "../types/strategy";

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

export async function fetchStrategyOptions() {
  const response = await apiClient.get<ApiResponse<StrategyOptionsPayload>>(
    "/api/v1/strategy/options"
  );
  return response.data;
}

export async function fetchStrategyReview(
  minAbsDelta = 1000,
  limit = 25,
  sleeve?: string
) {
  const params = sleeve
    ? { min_abs_delta: minAbsDelta, limit, sleeve }
    : { min_abs_delta: minAbsDelta, limit };

  const response = await apiClient.get<ApiResponse<StrategyReviewPayload>>(
    "/api/v1/strategy/review",
    { params }
  );
  return response.data;
}

export async function saveManualStrategyOverlay(
  payload: ManualStrategyOverlayUpsertRequest
) {
  const response = await apiClient.post<ApiResponse<ManualStrategyOverlayUpsertResult>>(
    "/api/v1/strategy/overlay/manual",
    payload
  );
  return response.data;
}