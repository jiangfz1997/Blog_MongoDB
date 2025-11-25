from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
import re

from pymongo import ReturnDocument


async def find_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[dict]:
    return await db.users.find_one({"email": email})

async def find_by_username(db: AsyncIOMotorDatabase, username: str) -> Optional[dict]:
    return await db.users.find_one({"username": username})


async def search_users_by_relevance(db: AsyncIOMotorDatabase, query: str, page:int=1, limit: int = 10):
    if not query:
        return []
    safe_query = re.escape(query)
    skip_count = (page - 1) * limit
    pipeline = [
        {
            "$match": {
                "username": {"$regex": safe_query, "$options": "i"}
            }
        },
        {
            "$addFields": {
                "match_score": {
                    "$switch": {
                        "branches": [
                            {
                                "case": {
                                    "$eq": [{"$toLower": "$username"}, query.lower()]
                                },
                                "then": 3
                            },
                            {
                                "case": {
                                    "$eq": [{"$indexOfCP": [{"$toLower": "$username"}, query.lower()]}, 0]
                                },
                                "then": 2
                            }
                        ],
                        "default": 1
                    }
                },
                "username_len": {"$strLenCP": "$username"}
            }
        },
        {
            "$sort": {
                "match_score": -1,
                "username_len": 1,
                "username": 1
            }
        },
        {"$skip": skip_count},
        {"$limit": limit},
        {"$project": {"match_score": 0, "username_len": 0, "email": 0, "password": 0}},
    ]

    users = await db.users.aggregate(pipeline).to_list(length=limit)

    total = await db.users.count_documents({"username": {"$regex": safe_query, "$options": "i"}})

    return users, total

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

async def update_user_info(db: AsyncIOMotorDatabase, user_id: ObjectId, update_fields: dict) -> dict:
    res = await db.users.find_one_and_update(
        {"_id": user_id},
        {"$set": update_fields},
        return_document = ReturnDocument.AFTER
    )
    return res

async def find_by_id_list(db: AsyncIOMotorDatabase, user_id_list: list) -> list:
    oid_list = []
    for uid in user_id_list:
        try:
            oid = ObjectId(uid)
            oid_list.append(oid)
        except Exception:
            continue
    projection = {
        "_id": 1,
        "username": 1,
        "avatar_url": 1,
    }
    cursor = db.users.find({"_id": {"$in": oid_list}}, projection)
    users = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
        users.append(doc)
    return users