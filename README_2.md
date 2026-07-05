# Fraud Detection System for Electronic Banking Transactions

A machine learning-based fraud detection system: FastAPI backend serving a trained Random Forest classifier, MongoDB Atlas for persistence, and a React/TypeScript dashboard for monitoring and testing predictions.

**Project topic:** *Development of a Machine Learning-Based Fraud Detection System for Electronic Banking Transactions*

## Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Motor (async MongoDB driver), scikit-learn |
| ML | Random Forest classifier, SMOTE for class imbalance |
| Database | MongoDB Atlas |
| Frontend | React, Vite, TypeScript, Tailwind CSS, Recharts |

## Repository structure

```
backend/
  app/
    config.py           # Environment loading
    db/mongo.py          # MongoDB client + connection check
    dependencies.py       # Static API key auth
    main.py               # FastAPI app entrypoint
    models/
      schemas.py          # Pydantic request/response contracts
      train_model.py       # Model training script (SMOTE + Random Forest)
    routers/
      predict.py           # POST /api/v1/predict
      analytics.py          # /summary, /model-performance, /trend
    services/
      ml_service.py         # Model loading + inference logic
  seed_data.py            # Populates DB with sampled real dataset rows
  check_db.py             # Diagnostic script for DB record counts
  requirements.txt

frontend/
  src/
    api/client.ts          # Typed fetch wrapper for backend API
    components/            # Shared UI: Layout, StatCard, VerdictBadge
    pages/                 # Dashboard, Predict, ModelPerformance, Trend
    types/index.ts         # TypeScript types mirroring backend schemas

setup_all.bat              # One-command setup for a fresh machine
SYSTEM_DOCUMENTATION.md    # Technical explanation: data flow, PCA, model methodology
```

## Setup

Run `setup_all.bat` from the repo root on a machine with Python 3.10+ and Node.js 18+ installed. It creates the backend virtual environment, installs all dependencies, and prepares `.env` files from the provided examples.

**After setup**, edit both env files with matching credentials:
- `backend/.env` → `MONGO_URI`, `DB_NAME`, `API_KEY`
- `frontend/.env` → `VITE_API_URL` (backend address), `VITE_API_KEY` (must match backend's `API_KEY`)

## Running

Two terminals, from the repo root:

```cmd
# Terminal 1 — backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

```cmd
# Terminal 2 — frontend
cd frontend
npm run dev
```

Open the URL shown by the frontend terminal (typically `http://localhost:5173`).

## Seeding demo data

```cmd
cd backend
python seed_data.py
```

Populates the database with sampled real rows from the source dataset, deliberately oversampled for fraud representation so all three action tiers (allow/review/block) are visible in the dashboard. **This ratio does not reflect real-world fraud prevalence** — see `SYSTEM_DOCUMENTATION.md` for the exact figures and reasoning.

## Key design notes

- **V1–V28 input features** are PCA-transformed components from the original dataset, not raw transaction attributes. See `SYSTEM_DOCUMENTATION.md` §2–4 for why, and why this system currently operates on held-out real dataset rows rather than arbitrary new live transactions.
- **Three-tier decision thresholds:** block ≥ 0.85, review 0.4–0.85, allow < 0.4. Reasonable defaults; not tuned against a precision-recall curve for this specific deployment — named as future work.
- **Authentication** is a static shared API key. Explicitly non-production — no rotation, no per-user scoping, no rate limiting.

## Known limitations

See `SYSTEM_DOCUMENTATION.md` §8 for the full list, including seed data distribution, threshold tuning status, and auth model — all stated explicitly rather than hidden, per the project's academic reporting requirements.
