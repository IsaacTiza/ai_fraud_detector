from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# ---------- /predict ----------

class TransactionInput(BaseModel):
    """
    What the client sends to POST /api/v1/predict.
    Time, Amount, V1-V28 are the actual model features (from the Kaggle dataset schema).
    location/device_id are metadata only — NOT fed into the model, logged for
    dashboard/UI context. The dataset's PCA transform (V1-V28) is not reproducible
    for arbitrary new transactions, so live demo inference uses held-out real rows
    from the source dataset rather than synthetic new feature vectors.
    """
    time: float = Field(..., ge=0, description="Seconds elapsed since first transaction in dataset")
    amount: float = Field(..., ge=0)
    v1: float; v2: float; v3: float; v4: float; v5: float
    v6: float; v7: float; v8: float; v9: float; v10: float
    v11: float; v12: float; v13: float; v14: float; v15: float
    v16: float; v17: float; v18: float; v19: float; v20: float
    v21: float; v22: float; v23: float; v24: float; v25: float
    v26: float; v27: float; v28: float
    location: Optional[str] = None
    device_id: Optional[str] = None


class PredictionResponse(BaseModel):
    """What POST /api/v1/predict returns — matches your locked contract exactly"""
    transaction_id: str
    fraud_probability: float
    action: Literal["allow", "review", "block"]


# ---------- transactions collection ----------

class TransactionRecord(BaseModel):
    """Full document shape stored in the transactions collection"""
    transaction_id: str
    time: float
    amount: float
    location: Optional[str] = None
    device_id: Optional[str] = None
    fraud_probability: float
    action: Literal["allow", "review", "block"]
    timestamp: datetime
    is_simulated: bool = False


# ---------- model_metrics collection ----------

class ModelMetrics(BaseModel):
    """One document per training run"""
    model_version: str
    trained_at: datetime
    recall: float
    precision: float
    f1: float
    roc_auc: float
    feature_importances: dict[str, float]


# ---------- feedback collection ----------

class FeedbackInput(BaseModel):
    """Analyst verdict on a flagged transaction"""
    transaction_id: str
    verdict: Literal["confirmed_fraud", "false_positive"]
    analyst_note: Optional[str] = None


# ---------- analytics responses ----------

class AnalyticsSummary(BaseModel):
    total_transactions: int
    flagged_count: int
    fraud_rate: float
    avg_fraud_probability: float


class TrendPoint(BaseModel):
    date: str
    total: int
    flagged: int


class TrendResponse(BaseModel):
    days: int
    data: list[TrendPoint]