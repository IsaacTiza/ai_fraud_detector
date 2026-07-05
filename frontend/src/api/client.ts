import type {
  TransactionInput,
  PredictResponse,
  SummaryResponse,
  ModelPerformanceResponse,
  TrendResponse,
} from "../types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
const API_KEY = import.meta.env.VITE_API_KEY ?? "";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`Request failed (${res.status}): ${text || res.statusText}`);
  }

  return res.json() as Promise<T>;
}

export function predictTransaction(payload: TransactionInput): Promise<PredictResponse> {
  return request<PredictResponse>("/api/v1/predict", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getSummary(): Promise<SummaryResponse> {
  return request<SummaryResponse>("/api/v1/analytics/summary");
}

export function getModelPerformance(): Promise<ModelPerformanceResponse> {
  return request<ModelPerformanceResponse>("/api/v1/analytics/model-performance");
}

export function getTrend(): Promise<TrendResponse> {
  return request<TrendResponse>("/api/v1/analytics/trend");
}
