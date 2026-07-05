"""
POST /api/v1/predict — the core inference endpoint.
Contract locked: returns {transaction_id, fraud_probability, action}.
"""

import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends

from app.dependencies import verify_api_key
from app.models.schemas import TransactionInput, PredictionResponse
from app.services.ml_service import predict_single
from app.db.mongo import transactions_collection

router = APIRouter(prefix="/api/v1", tags=["predict"])


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    transaction: TransactionInput,
    api_key: str = Depends(verify_api_key),
):
    features = transaction.model_dump()
    # features["v1"] = transaction.v1  # explicit, but model_dump() already includes these

    fraud_probability, action = predict_single(features)
    transaction_id = str(uuid.uuid4())

    # Persist the full record — logged regardless of action taken,
    # so model_metrics/dashboard analytics have real data to aggregate against.
    record = {
        "transaction_id": transaction_id,
        "time": transaction.time,
        "amount": transaction.amount,
        "location": transaction.location,
        "device_id": transaction.device_id,
        "fraud_probability": fraud_probability,
        "action": action,
        "timestamp": datetime.now(timezone.utc),
        "is_simulated": False,
    }
    await transactions_collection.insert_one(record)

    return PredictionResponse(
        transaction_id=transaction_id,
        fraud_probability=fraud_probability,
        action=action,
    )