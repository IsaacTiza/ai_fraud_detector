# Fraud Detection System — Data & Model Documentation

## 1. What the system takes as input

Every prediction request needs 30 numeric values:

| Field | Meaning |
|---|---|
| `Time` | Seconds elapsed since the first transaction in the dataset. Not a wall-clock timestamp — a relative offset. |
| `Amount` | Transaction amount in the dataset's currency unit. |
| `V1`–`V28` | 28 anonymized numerical features. These are **not raw transaction attributes** — they are the output of a PCA transform applied to the original, real features by the dataset's creators before public release. |

That last row is the one that needs the most explanation, and it's the one a supervisor will most likely probe.

## 2. Why V1–V28 exist instead of real features

The dataset (Kaggle "Credit Card Fraud Detection," originally released by the Machine Learning Group at Université Libre de Bruxelles) comes from real, anonymized European cardholder transactions over two days in September 2013. The original raw features — merchant category, cardholder history, location, device, IP, time-of-day patterns, transaction velocity, etc. — cannot legally or ethically be published, because they would make individual cardholders re-identifiable.

To solve this, the dataset creators ran **Principal Component Analysis (PCA)** on the original feature set before release, and published only the transformed output. Only `Time` and `Amount` were left untransformed because they don't expose personal identity on their own.

## 3. What PCA actually does (plain explanation)

PCA takes a set of correlated, human-readable features (say: merchant type, hour of day, distance from home, spending velocity, device fingerprint — dozens of raw signals) and re-expresses them as a new set of features that are:

- **Uncorrelated with each other** (each component captures a distinct axis of variation)
- **Ranked by how much variance they explain** (V1 captures the most variation in the original data, V2 the next most given it's orthogonal to V1, and so on)
- **Linear combinations of the originals** — each `Vn` is a weighted sum of many original features, not a stand-in for any single one of them

Critically: **the specific weights used in that transformation (the "loadings") were never published.** This is deliberate — without the transform matrix, there's no way to reverse `V1`–`V28` back into the original cardholder data. This is the privacy mechanism, not an incidental side effect.

## 4. Why this matters for your system's design

Because the PCA transform matrix is private and unpublished, **you cannot take a genuinely new, real-world transaction and correctly compute its V1–V28 values** — you don't have the formula the original researchers used. This is why:

- Your `/predict` endpoint accepts V1–V28 as direct numeric input rather than raw fields like `merchant_category` or `device_id`
- Your `seed_data.py` and demo/testing approach uses **held-out real rows from the source dataset**, not synthetically generated new transactions — because held-out real rows are the only rows that have valid, correctly-computed V1–V28 values
- The system as built is a **proof-of-concept demonstrating the ML methodology** (SMOTE class balancing, Random Forest classification, three-tier thresholding) on a real, standard benchmark dataset — not a drop-in production system that could ingest an arbitrary bank's live transaction stream today

## 5. How this WOULD be integrated with real-world live transactions (future work)

To deploy this against a real bank's live transaction feed, the pipeline would need to change at one specific point:

1. **Collect raw transaction features** from the bank's own systems: merchant category code, transaction hour, geolocation distance from cardholder's home/usual pattern, device fingerprint, IP reputation, velocity features (transactions in last hour/day), amount relative to the cardholder's historical average, etc.
2. **Fit your own PCA transform** on a large sample of this bank's historical labeled transaction data — this produces your own transform matrix, specific to your own feature set, which you *do* have and control.
3. **Apply that PCA transform to every new incoming transaction** in real time, producing your own 28 (or however many you choose) principal components.
4. **Feed those components into the already-trained Random Forest model** — the classifier itself doesn't need to be retrained just because the input pipeline changed, *provided* the new components are scaled and distributed similarly to the training data. In practice, you'd likely retrain the classifier on the new PCA space too, since a different raw feature set produces a different variance structure.
5. **Re-validate thresholds** (0.85 block / 0.4 review) against the new deployment's precision-recall tradeoff — thresholds tuned on this dataset don't automatically transfer to a different transaction population.

State this explicitly as future work in your report. It's not a weakness to name — a system that's honest about what it does and doesn't do is stronger than one that silently overclaims production-readiness.

## 6. Full technical workflow, end to end

```
Real-world raw transaction data (bank systems)
        ↓
[NOT IMPLEMENTED — future work]
Feature engineering + PCA transform (bank-specific)
        ↓
V1–V28, Time, Amount
        ↓
[THIS SYSTEM STARTS HERE]
POST /api/v1/predict  (FastAPI + Pydantic validation)
        ↓
ml_service.predict_single()
  → loads trained RandomForestClassifier (joblib)
  → outputs fraud_probability (0.0–1.0)
        ↓
Three-tier decision logic:
  probability >= 0.85  → "block"
  0.4 <= probability < 0.85  → "review"
  probability < 0.4  → "allow"
        ↓
Persisted to MongoDB (transactions collection)
        ↓
Surfaced via analytics endpoints:
  /summary            → aggregate counts, fraud rate
  /model-performance   → precision/recall/F1/ROC-AUC from training run
  /trend               → daily flagged vs. total, time series
        ↓
React frontend renders all of the above
```

## 7. Model training methodology (for defense Q&A)

- **Imbalance handling:** the true fraud rate in this dataset is ~0.17%. Training a classifier directly on this would produce a model that predicts "not fraud" for everything and still scores ~99.8% accuracy — a useless, high-accuracy-looking failure. **SMOTE (Synthetic Minority Oversampling Technique)** was applied to the training set only, generating synthetic minority-class (fraud) examples by interpolating between real fraud cases' feature vectors, to give the classifier enough fraud signal to learn from.
- **Split-before-SMOTE (the leakage fix):** SMOTE must be applied *after* the train/test split, not before. Applying it before splitting lets synthetic points derived from test-set fraud cases leak into the training set, artificially inflating test performance because the model has effectively "seen" interpolated versions of its own test answers. This was caught and fixed during development — mention this explicitly if asked about data leakage, it's a real methodological strength to have caught it.
- **Model choice — Random Forest:** chosen for robustness to the mixed-scale PCA features, resistance to overfitting via ensemble averaging, and built-in feature importance output (useful for the `feature_importances` field surfaced in `model_metrics`).
- **Metrics, at default 0.5 threshold:** Recall 0.847, Precision 0.610, F1 0.709, ROC AUC 0.985.
  - **Important — verify before your defense:** these numbers were computed at whatever threshold `train_model.py`'s evaluation step used. Your live system operates at 0.85/0.4, not 0.5. If asked "what's your precision at your actual deployed threshold," you need the recomputed numbers at those exact cutoffs, not the training-time metrics. If you haven't done this recalculation yet, it's the single most important remaining technical task before your defense — an examiner catching this mismatch live is a worse outcome than catching it yourself first.
- **Threshold justification:** 0.85 (block) and 0.4 (review) are reasonable, defensible starting points but were **not** tuned against a precision-recall curve for this specific deployment — state this as a named limitation, not a hidden gap. Future work: plot precision/recall across threshold sweep, pick values that reflect the actual cost asymmetry between false positives (blocking a legitimate customer) and false negatives (missing real fraud) for a banking context.

## 8. Named limitations — state these explicitly in your report

- Seed/demo data is deliberately oversampled for fraud representation (~9-10% flagged vs. true ~0.17% population rate) to make all three tiers visible in a demo. Does not reflect production traffic distribution.
- Thresholds (0.85/0.4) are reasonable defaults, not tuned against a validation precision-recall curve.
- Static API key authentication — no rotation, no per-user scoping, no rate limiting. Explicitly non-production.
- MongoDB Atlas IP whitelist — confirm and state current access policy (open vs. restricted) as a named tradeoff.
- V1–V28 cannot be computed for genuinely new real-world transactions without the original (unpublished) PCA transform — system operates on held-out real dataset rows for demonstration, not live arbitrary input.
- Feedback/analyst-verdict endpoint — confirm final status against your locked contract before submission; if cut, state it was descoped and why.
