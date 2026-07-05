// Mirrors app/models/schemas.py exactly, confirmed against real source.
export interface TransactionInput {
  time: number;
  amount: number;
  v1: number; v2: number; v3: number; v4: number; v5: number;
  v6: number; v7: number; v8: number; v9: number; v10: number;
  v11: number; v12: number; v13: number; v14: number; v15: number;
  v16: number; v17: number; v18: number; v19: number; v20: number;
  v21: number; v22: number; v23: number; v24: number; v25: number;
  v26: number; v27: number; v28: number;
}

export type ActionTier = "allow" | "review" | "block";

export interface PredictResponse {
  transaction_id: string;
  fraud_probability: number;
  action: ActionTier;
}

export interface SummaryResponse {
  total_transactions: number;
  flagged_count: number;
  fraud_rate: number;
  avg_fraud_probability: number;
}

export interface ModelPerformanceResponse {
  model_version: string;
  trained_at: string;
  recall: number;
  precision: number;
  f1: number;
  roc_auc: number;
  feature_importances: Record<string, number>;
}

// CORRECTED: backend returns { days, data: TrendPoint[] }, not a bare array.
export interface TrendPoint {
  date: string;
  total: number;
  flagged: number;
}

export interface TrendResponse {
  days: number;
  data: TrendPoint[];
}
