"""
Generates synthetic historical volume by sampling real rows from the
Kaggle dataset (not synthetic feature vectors — real, held-out rows),
backdating them across N days, and running them through the actual
/predict logic so is_simulated=True records exercise the same inference
+ persistence path as live traffic.

Fraud cases are DELIBERATELY oversampled relative to the true 0.173%
population rate. A pure random sample of 400 rows would statistically
yield close to zero fraud cases, making the dashboard look like the
system detects nothing. This is a named, explicit tradeoff — documented
here and should be stated in the report: seed data distribution ≠
production traffic distribution.
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone

import pandas as pd

from app.services.ml_service import load_model, predict_single
from app.db.mongo import transactions_collection

DATA_PATH = "data/creditcard.csv"
NUM_TRANSACTIONS = 400
NUM_FRAUD_SAMPLE = 40  # ~10% of seed data — visible across all action tiers
DAYS_BACK = 30

LOCATIONS = ["Lagos", "Abuja", "Port Harcourt", "Ibadan", "Kano", "London", "New York"]


async def clear_seeded_data():
    result = await transactions_collection.delete_many({"is_simulated": True})
    print(f"Cleared {result.deleted_count} previously seeded transactions.")


async def seed():
    load_model()
    await clear_seeded_data()

    df = pd.read_csv(DATA_PATH)

    fraud_rows = df[df["Class"] == 1]
    normal_rows = df[df["Class"] == 0]

    num_normal_sample = NUM_TRANSACTIONS - NUM_FRAUD_SAMPLE

    fraud_sample = fraud_rows.sample(n=NUM_FRAUD_SAMPLE, random_state=None)
    normal_sample = normal_rows.sample(n=num_normal_sample, random_state=None)

    sample = pd.concat([fraud_sample, normal_sample]).sample(frac=1).reset_index(drop=True)

    records = []
    now = datetime.now(timezone.utc)

    for _, row in sample.iterrows():
        features = {"time": row["Time"], "amount": row["Amount"]}
        features.update({f"v{i}": row[f"V{i}"] for i in range(1, 29)})

        fraud_probability, action = predict_single(features)

        backdated_time = now - timedelta(
            days=random.uniform(0, DAYS_BACK),
            hours=random.uniform(0, 24),
        )

        records.append({
            "transaction_id": str(uuid.uuid4()),
            "time": row["Time"],
            "amount": row["Amount"],
            "location": random.choice(LOCATIONS),
            "device_id": f"device-{random.randint(1000, 9999)}",
            "fraud_probability": fraud_probability,
            "action": action,
            "timestamp": backdated_time,
            "is_simulated": True,
        })

    result = await transactions_collection.insert_many(records)
    print(f"Inserted {len(result.inserted_ids)} seeded transactions.")

    action_counts = {}
    for r in records:
        action_counts[r["action"]] = action_counts.get(r["action"], 0) + 1
    print(f"Action breakdown: {action_counts}")


if __name__ == "__main__":
    asyncio.run(seed())