from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from pymongo import ReturnDocument


async def add_blog(db: AsyncIOMotorDatabase, blog_doc: dict) -> dict:
    if "tags" not in blog_doc:
        blog_doc["tags"] = []
    if "view_count" not in blog_doc:
        blog_doc["view_count"] = 0

    res = await db.blogs.insert_one(blog_doc)
    created = await db.blogs.find_one({"_id": res.inserted_id})
    # serialize
    created["id"] = str(created["_id"])
    created.pop("_id", None)
    return created


async def update_blog(db: AsyncIOMotorDatabase, blog_id: str, blog_doc: dict) -> Optional[dict]:
    update_fields = {}
    if "title" in blog_doc:
        update_fields["title"] = blog_doc["title"]
    if "content" in blog_doc:
        update_fields["content"] = blog_doc["content"]
    if "tags" in blog_doc:
        update_fields["tags"] = blog_doc["tags"]

    update_fields["updated_at"] = datetime.utcnow()

    await db.blogs.update_one({"_id": ObjectId(blog_id)}, {"$set": update_fields})
    updated = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    if not updated:
        return None
    updated["id"] = str(updated["_id"])
    updated.pop("_id", None)
    return updated


async def delete_blog(db: AsyncIOMotorDatabase, blog_id: str) -> bool:
    res = await db.blogs.delete_one({"_id": ObjectId(blog_id)})
    return res.deleted_count == 1


async def find_blog_by_id(db: AsyncIOMotorDatabase, blog_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(blog_id)
    except Exception:
        return None

    doc = await db.blogs.find_one({"_id": oid})
    if not doc:
        return None

    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    if "tags" not in doc:
        doc["tags"] = []
    if "view_count" not in doc:
        doc["view_count"] = 0

    return doc

def _serialize(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        #"content": doc["content"],
        "author_id": doc["author_id"],
        "created_at": doc["created_at"],
        "updated_at": doc.get("updated_at"),
        "tags": doc.get("tags", []),
        "view_count": doc.get("view_count", 0),
    }

async def list_blogs_by_author(
    db: AsyncIOMotorDatabase,
    author_id: str,
    limit: int = 10,
    skip: int = 0,
) -> List[dict]:
    cursor = (
        db.blogs
        .find({"author_id": author_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    items: List[dict] = []
    async for doc in cursor:
        items.append(_serialize(doc))
    return items

async def count_blogs_by_author(db: AsyncIOMotorDatabase, author_id: str) -> int:
    return await db.blogs.count_documents({"author_id": author_id})


async def search_blogs_by_title(
    db: AsyncIOMotorDatabase,
    keyword: str,
    skip: int = 0,
    limit: int = 10,
) -> List[dict]:
    """
    Search blogs whose titles contain the keyword (case-insensitive).
    Return the list of serialized blogs.
    """
    query = {
        "title": {
            "$regex": keyword,
            "$options": "i"   # i = ignore case
        }
    }

    cursor = (
        db.blogs
        .find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    items: List[dict] = []
    async for doc in cursor:
        items.append(_serialize(doc))
    return items


async def count_blogs_by_title(db: AsyncIOMotorDatabase,keyword: str,) -> int:
    """
    Return the total number of blogs whose titles match the keyword.
    """
    query = {
        "title": {
            "$regex": keyword,
            "$options": "i"
        }
    }
    return await db.blogs.count_documents(query)

async def get_hottest_tags(db: AsyncIOMotorDatabase,limit: int = 10,) -> List[dict]:
    """
    Aggregate and compute the currently hottest tags.
    Sort tags by the number of blogs that use them in descending order, and return the top limit tags.
    """
    pipeline = [
        {"$unwind": "$tags"},
        {
            "$group": {
                "_id": "$tags",
                "blog_count": {"$sum": 1},
            }
        },
        {"$sort": {"blog_count": -1}},
        {"$limit": limit},
    ]

    cursor = db.blogs.aggregate(pipeline)
    results: List[dict] = []
    async for doc in cursor:
        # Keep result here; it will be converted to HottestTagResponse in the service layer.
        results.append(doc)
    return results

# read blog
async def find_blog_by_id_and_inc_view(db: AsyncIOMotorDatabase, blog_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(blog_id)
    except Exception:
        return None

    doc = await db.blogs.find_one_and_update(
        {"_id": oid},
        {"$inc": {"view_count": 1}},
        return_document=ReturnDocument.AFTER,
    )
    if not doc:
        return None

    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    if "tags" not in doc:
        doc["tags"] = []
    if "view_count" not in doc:
        doc["view_count"] = 0
    return doc

async def list_blogs_by_views(
    db: AsyncIOMotorDatabase,
    limit: int = 10,
    skip: int = 0,
) -> List[dict]:
    cursor = (
        db.blogs
        .find({}, {"content": 0})
        .sort("view_count", -1)
        .skip(skip)
        .limit(limit)
    )

    items: List[dict] = []
    async for doc in cursor:
        items.append({
            "id": str(doc["_id"]),
            "title": doc["title"],
            "author_id": doc["author_id"],
            "created_at": doc["created_at"],
            "updated_at": doc.get("updated_at"),
            "tags": doc.get("tags", []),
            "view_count": doc.get("view_count", 0),
        })
    return items