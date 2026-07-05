from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

transactions_collection = db["transactions"]
model_metrics_collection = db["model_metrics"]
feedback_collection = db["feedback"]


async def ping_database() -> bool:
    """Verify the connection is alive. Used at startup and in a health check route."""
    try:
        await client.admin.command("ping")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False