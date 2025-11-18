from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


def _serialize(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "blog_id": str(doc["blog_id"]),
        "author_id": str(doc["author_id"]),
        "parent_id": str(doc["parent_id"]) if doc.get("parent_id") else None,
        "content": doc["content"],
        "created_at": doc["created_at"],
    }

async def add_comment(db: AsyncIOMotorDatabase, comment_doc: dict) -> dict:
    res = await db.comments.insert_one(comment_doc)
    created = await db.comments.find_one({"_id": res.inserted_id})
    return _serialize(created)

# Get single comment by ID
async def find_comment_by_id(db, comment_id: str) -> Optional[dict]:
    try:
        oid = ObjectId(comment_id)
    except Exception:
        return None

    doc = await db.comments.find_one({"_id": oid})
    if not doc:
        return None

    return _serialize(doc)

# List all comments under a blog
async def list_comments_by_blog(db: AsyncIOMotorDatabase,blog_id: str) -> List[dict]:
    # # convert str → ObjectId
    # try:
    #     blog_oid = ObjectId(blog_id)
    # except:
    #     blog_oid = blog_id

    cursor = db.comments.find({"blog_id": blog_id},sort=[("created_at", 1)])

    items: List[dict] = []
    async for doc in cursor:
        items.append(_serialize(doc))
    return items


# Delete comment tree (comment + replies)
async def _collect_descendant_ids(db: AsyncIOMotorDatabase,root_id: str,) -> List[str]:
    """
    root_id: 根评论的 id 字符串（比如 "691bc253ee7373..."）
    返回值: 所有子孙评论的 id 字符串列表
    """
    to_visit = [root_id]
    all_ids: List[str] = []

    while to_visit:
        current_batch = to_visit
        to_visit = []

        cursor = db.comments.find({"parent_id": {"$in": current_batch}},{"_id": 1},)

        async for doc in cursor:
            child_id_str = str(doc["_id"])
            all_ids.append(child_id_str)
            to_visit.append(child_id_str)

    return all_ids


async def delete_comment_tree(db: AsyncIOMotorDatabase,comment_id: str) -> bool:

    try:
        root_oid = ObjectId(comment_id)
    except Exception:
        return False

    root = await db.comments.find_one({"_id": root_oid})
    if not root:
        return False

    # 先用字符串 id 找所有子孙
    descendant_ids = await _collect_descendant_ids(db, comment_id)

    # 所有要删的 id（字符串转 ObjectId）
    all_ids_str = [comment_id] + descendant_ids
    all_oids = [ObjectId(cid) for cid in all_ids_str]

    res = await db.comments.delete_many({"_id": {"$in": all_oids}})
    return res.deleted_count > 0