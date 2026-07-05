import asyncio
from app.db.mongo import transactions_collection

async def main():
    doc = await transactions_collection.find_one(
        {"transaction_id": "44786d68-bdc7-4eed-8f02-79c20d86da17"}
    )
    print(doc)

asyncio.run(main())