from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime


async def add_blog(db: AsyncIOMotorDatabase, blog_doc: dict) -> dict:
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
    return doc

def _serialize(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "title": doc["title"],
        "content": doc["content"],
        "author_id": doc["author_id"],
        "created_at": doc["created_at"],
        "updated_at": doc.get("updated_at"),
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
    搜索标题包含关键字的博客（大小写不敏感）。
    返回 serialize 后的博客列表。
    """
    # 构造大小写不敏感的搜索条件
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
    返回匹配标题关键字的博客总数。
    """
    query = {
        "title": {
            "$regex": keyword,
            "$options": "i"
        }
    }
    return await db.blogs.count_documents(query)