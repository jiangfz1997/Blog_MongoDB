from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

async def find_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[dict]:
    return await db.users.find_one({"email": email})

async def insert_user(db: AsyncIOMotorDatabase, user_doc: dict) -> dict:
    res = await db.users.insert_one(user_doc)
    created = await db.users.find_one({"_id": res.inserted_id})
    # serialize
    created["id"] = str(created["_id"])
    created.pop("_id", None)
    created.pop("password", None)
    return created