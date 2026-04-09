import { apiClient } from "./client";
import type { ApiResponse } from "../types/api";
import type {
  FullSyncActionResult,
  FxSyncActionResult,
  SyncActionResult,
} from "../types/imports";

export async function runKiwoomSync(): Promise<ApiResponse<SyncActionResult>> {
  const response = await apiClient.post<ApiResponse<SyncActionResult>>("/api/v1/sync/kiwoom");
  return response.data;
}

export async function runFxSync(): Promise<ApiResponse<FxSyncActionResult>> {
  const response = await apiClient.post<ApiResponse<FxSyncActionResult>>("/api/v1/sync/fx");
  return response.data;
}

export async function runFullSync(): Promise<ApiResponse<FullSyncActionResult>> {
  const response = await apiClient.post<ApiResponse<FullSyncActionResult>>("/api/v1/sync/full");
  return response.data;
}

export async function importUsHoldingsCsv(
  file: File,
  usdCash: string
): Promise<ApiResponse<SyncActionResult>> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("usd_cash", usdCash);

  const response = await apiClient.post<ApiResponse<SyncActionResult>>(
    "/api/v1/import/us-holdings",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}