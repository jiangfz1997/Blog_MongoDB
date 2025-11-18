from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

async def find_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[dict]:
    doc = await db.users.find_one({"email": email})
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc
    #return await db.users.find_one({"email": email})

async def find_by_username(db: AsyncIOMotorDatabase, username: str) -> Optional[dict]:
    doc = await db.users.find_one({"username": username})
    if not doc:
        return None
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc
    #return await db.users.find_one({"username": username})

async def find_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None

    doc = await db.users.find_one({"_id": oid})
    if not doc:
        return None

    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc

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