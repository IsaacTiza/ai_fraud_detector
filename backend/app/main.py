from fastapi import FastAPI
from app.services.ml_service import load_model
from app.db.mongo import ping_database
from app.routers import predict, analytics
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(predict.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def startup():
    load_model()
    connected = await ping_database()
    if not connected:
        print("[WARNING] MongoDB connection failed at startup.")


@app.get("/health")
async def health():
    return {"status": "ok"}