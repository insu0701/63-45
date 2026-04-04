import { apiClient } from "./client";
import type { ApiResponse } from "../types/api";
import type {
  CountryAllocationItem,
  CurrencyAllocationItem,
  SectorAllocationItem,
  SleeveAllocationItem,
} from "../types/allocation";

export async function fetchSleeveAllocation(): Promise<ApiResponse<SleeveAllocationItem[]>> {
  const response = await apiClient.get<ApiResponse<SleeveAllocationItem[]>>(
    "/api/v1/allocation/sleeve"
  );
  return response.data;
}

export async function fetchCountryAllocation(): Promise<ApiResponse<CountryAllocationItem[]>> {
  const response = await apiClient.get<ApiResponse<CountryAllocationItem[]>>(
    "/api/v1/allocation/country"
  );
  return response.data;
}

export async function fetchSectorAllocation(): Promise<ApiResponse<SectorAllocationItem[]>> {
  const response = await apiClient.get<ApiResponse<SectorAllocationItem[]>>(
    "/api/v1/allocation/sector"
  );
  return response.data;
}

export async function fetchCurrencyAllocation(): Promise<ApiResponse<CurrencyAllocationItem[]>> {
  const response = await apiClient.get<ApiResponse<CurrencyAllocationItem[]>>(
    "/api/v1/allocation/currency"
  );
  return response.data;
}