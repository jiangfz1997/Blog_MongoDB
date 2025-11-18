from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

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

#change password
async def update_password_hash(db: AsyncIOMotorDatabase, user_id: ObjectId, new_hash: str) -> bool:
    res = await db.users.update_one({"_id": user_id}, {"$set": {"password": new_hash}})
    return res.matched_count == 1