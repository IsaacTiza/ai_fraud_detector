"""
Loads the most recently trained model artifact and exposes prediction
functions to the rest of the app. Picks the latest model by filename
timestamp, so retraining (train_model.py) and serving are fully decoupled —
retrain any time, restart the API, it picks up the new version automatically.
"""

import joblib
import numpy as np
from pathlib import Path
import pandas as pd

ARTIFACTS_DIR = Path(__file__).resolve().parents[2] / "artifacts"

FEATURE_ORDER = ["Time", "Amount"] + [f"V{i}" for i in range(1, 29)]

_model = None
_model_version = None


def _find_latest_model_path() -> Path:
    candidates = sorted(ARTIFACTS_DIR.glob("model_v*.joblib"))
    if not candidates:
        raise FileNotFoundError(
            f"No trained model found in {ARTIFACTS_DIR}. "
            f"Run `python -m app.models.train_model` first."
        )
    return candidates[-1]  # timestamp-named files sort chronologically


def load_model():
    """Called once at app startup. Loads the latest model into memory."""
    global _model, _model_version
    path = _find_latest_model_path()
    _model = joblib.load(path)
    _model_version = path.stem.replace("model_", "")
    print(f"[ml_service] Loaded model version: {_model_version} from {path.name}")
    return _model_version


def get_loaded_version() -> str:
    if _model_version is None:
        raise RuntimeError("Model not loaded yet. Call load_model() at startup.")
    return _model_version


import pandas as pd

def predict_single(features: dict) -> tuple[float, str]:
    """
    features: dict with keys matching FEATURE_ORDER (time, amount, v1..v28
    from TransactionInput, lowercase per your schema).
    Returns (fraud_probability, action).
    """
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() at startup.")

    ordered_values = [
        features["time"], features["amount"]
    ] + [features[f"v{i}"] for i in range(1, 29)]

    X = pd.DataFrame([ordered_values], columns=FEATURE_ORDER)
    probability = float(_model.predict_proba(X)[0, 1])

    action = _decide_action(probability)
    return probability, action


def _decide_action(probability: float) -> str:
    """
    Three-tier decision boundary. Thresholds are a deliberate, named choice —
    not the default 0.5 cutoff — because this dataset's extreme imbalance
    means a single threshold poorly separates genuine uncertainty from
    confident predictions. Tune these against your own validation results
    if they don't match your risk tolerance.
    """
    if probability >= 0.85:
        return "block"
    elif probability >= 0.4:
        return "review"
    else:
        return "allow"