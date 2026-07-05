"""
Read-only analytics endpoints. All pull live from MongoDB — nothing
hardcoded. model-performance reads the LATEST document in model_metrics
(the training run, not the live-loaded model in memory), so it reflects
whatever is in the database even if ml_service hasn't been restarted yet.
"""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import verify_api_key
from app.models.schemas import AnalyticsSummary, ModelMetrics, TrendResponse, TrendPoint
from app.db.mongo import transactions_collection, model_metrics_collection

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(api_key: str = Depends(verify_api_key)):
    total = await transactions_collection.count_documents({})
    flagged = await transactions_collection.count_documents(
        {"action": {"$in": ["review", "block"]}}
    )

    pipeline = [{"$group": {"_id": None, "avg_prob": {"$avg": "$fraud_probability"}}}]
    result = await transactions_collection.aggregate(pipeline).to_list(length=1)
    avg_prob = result[0]["avg_prob"] if result else 0.0

    fraud_rate = flagged / total if total > 0 else 0.0

    return AnalyticsSummary(
        total_transactions=total,
        flagged_count=flagged,
        fraud_rate=fraud_rate,
        avg_fraud_probability=avg_prob,
    )


@router.get("/model-performance", response_model=ModelMetrics)
async def get_model_performance(api_key: str = Depends(verify_api_key)):
    latest = await model_metrics_collection.find_one(
        sort=[("trained_at", -1)]
    )
    if latest is None:
        raise HTTPException(status_code=404, detail="No trained model metrics found.")
    return ModelMetrics(**latest)


@router.get("/trend", response_model=TrendResponse)
async def get_trend(days: int = 7, api_key: str = Depends(verify_api_key)):
    since = datetime.now(timezone.utc) - timedelta(days=days)

    pipeline = [
        {"$match": {"timestamp": {"$gte": since}}},
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "total": {"$sum": 1},
                "flagged": {
                    "$sum": {
                        "$cond": [{"$in": ["$action", ["review", "block"]]}, 1, 0]
                    }
                },
            }
        },
        {"$sort": {"_id": 1}},
    ]
    results = await transactions_collection.aggregate(pipeline).to_list(length=None)

    data = [
        TrendPoint(date=r["_id"], total=r["total"], flagged=r["flagged"])
        for r in results
    ]
    return TrendResponse(days=days, data=data)
