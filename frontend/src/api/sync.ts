import { apiClient } from "./client";
import type { ApiResponse } from "../types/api";
import type { SyncStatusPayload } from "../types/sync";

export async function fetchSyncStatus(): Promise<ApiResponse<SyncStatusPayload>> {
  const response = await apiClient.get<ApiResponse<SyncStatusPayload>>("/api/v1/sync/status");
  return response.data;
}