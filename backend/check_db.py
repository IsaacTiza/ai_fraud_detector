import asyncio
from app.db.mongo import transactions_collection


async def check():
    total = await transactions_collection.count_documents({})
    print(f"Total docs in collection: {total}")

    non_simulated = await transactions_collection.count_documents({"is_simulated": {"$ne": True}})
    print(f"Non-simulated docs: {non_simulated}")

    sample = await transactions_collection.find().sort("_id", -1).limit(3).to_list(length=3)
    for doc in sample:
        print(doc)


if __name__ == "__main__":
    asyncio.run(check())