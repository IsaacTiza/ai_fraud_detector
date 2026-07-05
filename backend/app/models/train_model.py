"""
Offline training script — decoupled from the FastAPI serving layer.
Run manually: python -m app.models.train_model
Answers the viva question "what happens when fraud patterns change?" —
retraining happens here, independently, and the serving layer picks up
the new model by version without any API downtime.
"""

import joblib
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score, precision_score, f1_score, roc_auc_score
from imblearn.over_sampling import SMOTE
from pymongo import MongoClient

from app.config import settings

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "creditcard.csv"
ARTIFACTS_DIR = Path(__file__).resolve().parents[2] / "artifacts"

FEATURE_COLUMNS = ["Time", "Amount"] + [f"V{i}" for i in range(1, 29)]
TARGET_COLUMN = "Class"


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}. Download from Kaggle "
            f"and place it there before training."
        )
    return pd.read_csv(DATA_PATH)


def train_and_evaluate():
    df = load_data()
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    # --- CRITICAL: split BEFORE any resampling ---
    # SMOTE must never see the test set. Applying it before the split
    # leaks synthetic-neighbor information into "unseen" data and
    # inflates recall/F1 — the exact metrics this project depends on
    # being trustworthy. This ordering is the fix for that risk.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    print(f"Train set: {X_train.shape[0]} rows, fraud rate: {y_train.mean():.4%}")
    print(f"Test set:  {X_test.shape[0]} rows, fraud rate: {y_test.mean():.4%}")

    # SMOTE fit ONLY on training data
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    print(f"After SMOTE: {X_train_resampled.shape[0]} rows, "
          f"fraud rate: {y_train_resampled.mean():.4%}")

    # Random Forest chosen over XGBoost: interpretable via feature_importances_,
    # lower overfitting risk under time pressure, easier to defend in viva.
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        class_weight=None,  # SMOTE already balances the training set — combining
                            # with class_weight would double-correct for imbalance
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train_resampled, y_train_resampled)

    # Evaluate on the UNTOUCHED, real-distribution test set
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    recall = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)

    print(f"\nRecall:    {recall:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"F1:        {f1:.4f}")
    print(f"ROC AUC:   {roc_auc:.4f}")

    feature_importances = dict(
        zip(FEATURE_COLUMNS, model.feature_importances_.tolist())
    )

    # --- Model versioning, tied to model_metrics ---
    # Version = UTC timestamp. Same version string goes into both the
    # artifact filename and the metrics document, so any stored model
    # file can be traced back to the exact metrics it produced, and
    # ml_service.py can log which version it loaded at startup.
    model_version = datetime.now(timezone.utc).strftime("v%Y%m%d_%H%M%S")

    ARTIFACTS_DIR.mkdir(exist_ok=True)
    model_path = ARTIFACTS_DIR / f"model_{model_version}.joblib"
    joblib.dump(model, model_path)
    print(f"\nModel saved: {model_path}")

    # Write metrics to MongoDB — synchronous client here, this is a
    # standalone offline script, not the async FastAPI request path.
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.DB_NAME]
    db["model_metrics"].insert_one({
        "model_version": model_version,
        "trained_at": datetime.now(timezone.utc),
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "roc_auc": roc_auc,
        "feature_importances": feature_importances,
    })
    client.close()
    print(f"Metrics logged to model_metrics collection, version {model_version}")

    return model_version


if __name__ == "__main__":
    train_and_evaluate()