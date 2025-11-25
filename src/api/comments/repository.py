from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


def _serialize(doc: dict) -> dict:
    """
    Convert the raw comment document returned by MongoDB into a Python dict and unify the field format.
    """
    return {
        "id": str(doc["_id"]),
        "blog_id": str(doc["blog_id"]),
        "author_id": str(doc["author_id"]),
        "is_root": bool(doc.get("is_root", False)),
        "root_id": str(doc.get("root_id")) if doc.get("root_id") else str(doc["_id"]),
        "parent_id": str(doc["parent_id"]) if doc.get("parent_id") else None,
        "reply_to_comment_id": (str(doc["reply_to_comment_id"]) if doc.get("reply_to_comment_id") else None),
        "reply_to_username": doc.get("reply_to_username"),
        "content": doc["content"],
        "created_at": doc["created_at"],
    }

async def add_comment(db: AsyncIOMotorDatabase, comment_doc: dict, blog_id: str) -> dict:
    res = await db.comments.insert_one(comment_doc)
    if comment_doc.get("is_root") and not comment_doc.get("root_id"):
        await db.comments.update_one(
            {"_id": res.inserted_id},
            {"$set": {"root_id": str(res.inserted_id)}},
        )
    created = await db.comments.find_one({"_id": res.inserted_id})
    await db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$inc": {"comment_count": 1}}  # 原子加一，并发安全
    )
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

async def delete_root_thread(db: AsyncIOMotorDatabase, root_id: str, blog_id:str) -> int:
    res = await db.comments.delete_many({"root_id": root_id})
    await db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$inc": {"comment_count": -res.deleted_count}}
    )
    return res.deleted_count


async def delete_single_comment(db: AsyncIOMotorDatabase, comment_id: str, blog_id: str) -> bool:
    """
    Delete a single non-root comment.
    Do not perform cascade deletion; other replies remain preserved.
    """
    try:
        oid = ObjectId(comment_id)
    except Exception:
        return False

    res = await db.comments.delete_one({"_id": oid})
    await db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$inc": {"comment_count": -1}}
    )
    return res.deleted_count == 1


async def list_root_comments_by_blog(
    db: AsyncIOMotorDatabase,
    blog_id: str,
    skip: int = 0,
    limit: int = 10,
) -> List[dict]:
    """
    List root comments (excluding replies) of a blog with pagination.
    Used for paginating the root comment list:
    - Filter: blog_id = blog_id, is_root = True
    - Sort: by created_at in ascending order (earliest first), or change to descending if needed
    - Pagination: skip / limit
    """
    cursor = (
        db.comments
        .find({"blog_id": blog_id, "is_root": True})
        .sort("created_at", 1)
        .skip(skip)
        .limit(limit)
    )

    items: List[dict] = []
    async for doc in cursor:
        items.append(_serialize(doc))
    return items


async def count_root_comments_by_blog(db: AsyncIOMotorDatabase, blog_id: str) -> int:
    """
    Count the total number of root comments under a blog.
    Used as the total for root comment pagination.
    """
    return await db.comments.count_documents({"blog_id": blog_id, "is_root": True})


async def list_replies_by_root(
    db: AsyncIOMotorDatabase,
    root_id: str,
    skip: int = 0,
    limit: int = 10,
) -> List[dict]:
    """
    Paginate all non-root comments (flat replies) under a given root comment.
    root_id = given root_id
    is_root = False
    Sort by created_at in ascending order to preserve the conversation timeline.
    """
    cursor = (
        db.comments
        .find({"root_id": root_id, "is_root": False})
        .sort("created_at", 1)
        .skip(skip)
        .limit(limit)
    )

    items: List[dict] = []
    async for doc in cursor:
        items.append(_serialize(doc))
    return items


async def count_replies_by_root(db: AsyncIOMotorDatabase, root_id: str) -> int:
    """
    Count the total number of non-root comments under a root comment.
    Used as the total for non-root comment pagination.
    """
    return await db.comments.count_documents({"root_id": root_id, "is_root": False})








#comment tree#
# List all comments under a blog
# async def list_comments_by_blog(db: AsyncIOMotorDatabase,blog_id: str) -> List[dict]:
#     cursor = db.comments.find({"blog_id": blog_id},sort=[("created_at", 1)])
#
#     items: List[dict] = []
#     async for doc in cursor:
#         items.append(_serialize(doc))
#     return items
#

# Delete comment tree (comment + replies)
# async def _collect_descendant_ids(db: AsyncIOMotorDatabase,root_id: str,) -> List[str]:
#     to_visit = [root_id]
#     all_ids: List[str] = []
#
#     while to_visit:
#         current_batch = to_visit
#         to_visit = []
#
#         cursor = db.comments.find({"parent_id": {"$in": current_batch}},{"_id": 1},)
#
#         async for doc in cursor:
#             child_id_str = str(doc["_id"])
#             all_ids.append(child_id_str)
#             to_visit.append(child_id_str)
#
#     return all_ids
#
#
# async def delete_comment_tree(db: AsyncIOMotorDatabase,comment_id: str) -> bool:
#
#     try:
#         root_oid = ObjectId(comment_id)
#     except Exception:
#         return False
#
#     root = await db.comments.find_one({"_id": root_oid})
#     if not root:
#         return False
#
#     descendant_ids = await _collect_descendant_ids(db, comment_id)
#
#     all_ids_str = [comment_id] + descendant_ids
#     all_oids = [ObjectId(cid) for cid in all_ids_str]
#
#     res = await db.comments.delete_many({"_id": {"$in": all_oids}})
#     return res.deleted_count > 0