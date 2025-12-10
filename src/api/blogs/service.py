import asyncio
import json
from datetime import datetime

from bson import ObjectId

from src.db.mongo import db
from . import repository
from src.api.blogs.schemas import *
from fastapi import HTTPException, status
from typing import Dict, Any, Optional
from src.api.users import repository as user_repository
from src.logger import get_logger
from src.core.redis import redis_client

CACHE_KEY = "hot_tags:top10"
_is_refreshing = False
logger = get_logger()
async def create_blog(author_id: str, blog_in: BlogCreate) -> dict:
    blog_doc = {
        "title": blog_in.title,
        "content": blog_in.content,
        "author_id": author_id,                 # from JWT
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "tags": blog_in.tags,
        "view_count": 0,
        "like_count": 0,
        "liked_by": [],
    }
    created = await asyncio.wait_for(repository.add_blog(db, blog_doc), timeout=5)
    user = await user_repository.find_by_id(db, created["author_id"])
    user_name = user["username"] if user else "Unknown"
    created["author_username"] = user_name
    return created

async def edit_blog(blog_id: str, author_id: str, update_fields: Dict[str, Any]) -> dict:
    """
    Only author can edit blog
    """
    # check blog existed
    existing = await repository.find_blog_by_id(db, blog_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    # only author can edit
    if existing["author_id"] != author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # if nothing update,ignore
    filtered: Dict[str, Any] = {}
    if "title" in update_fields and update_fields["title"] is not None:
        filtered["title"] = update_fields["title"]
    if "content" in update_fields and update_fields["content"] is not None:
        filtered["content"] = update_fields["content"]
    if "tags" in update_fields and update_fields["tags"] is not None:
        filtered["tags"] = update_fields["tags"]

    if not filtered:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")


    updated = await asyncio.wait_for(repository.update_blog(db, blog_id, filtered), timeout=5)
    if not updated:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update failed")
    user = await user_repository.find_by_id(db, updated["author_id"])
    user_name = user["username"] if user else "Unknown"
    updated["author_username"] = user_name
    return updated


async def remove_blog(blog_id: str, author_id: str) -> None:
    """
    Only author can delete blog
    """
    # check blog existed
    existing = await repository.find_blog_by_id(db, blog_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")

    # only author can delete
    if existing["author_id"] != author_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    ok = await asyncio.wait_for(repository.delete_blog(db, blog_id), timeout=5)
    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Delete failed")

#get blog by blog_id, read blog detail content,increase view count
async def get_blog(blog_id: str, user_id: str = None) -> dict:
    doc = await repository.find_blog_by_id_and_inc_view(db, blog_id, user_id)
    # Batch query author usernames (to avoid repeated database lookups).
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    user = await user_repository.find_by_id(db, doc["author_id"])
    user_name = user["username"] if user else "Unknown"
    doc["author_username"] = user_name
    logger.debug(f"Get blog detail: {doc}")
    return doc

# get blog preview without content
async def get_blog_preview(blog_id: str) -> BlogPreviewResponse:
    """
    get blog without detail content
    """
    doc = await repository.find_blog_by_id(db, blog_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    return BlogPreviewResponse(
        id=doc["id"],
        title=doc["title"],
        author_id=doc["author_id"],
        created_at=doc["created_at"],
        updated_at=doc.get("updated_at"),
        tags=doc.get("tags", []),
    )

#get blog by author
async def list_author_blogs(author_id: str, page: int = 1, size: int = 10, exclude_blog_id: str=None) -> Dict[str, Any]:
    page = max(page, 1)
    size = max(min(size, 50), 1)
    skip = (page - 1) * size

    items = await repository.list_blogs_by_author(db, author_id, limit=size, skip=skip, exclude = exclude_blog_id)
    total = await repository.count_blogs_by_author(db, author_id)
    return {
        "items": items,
        "page": page,
        "size": size,
        "total": total,
        "has_next": page * size < total,
    }

# hottest blog tagSort tags by the number of blogs that use them, in descending order.
async def get_hottest_tags(limit: int = 10) -> List[HottestTagResponse]:
    """
    Sort tags by the number of blogs that use them, in descending order.
    """
    global _is_refreshing
    if _is_refreshing: # prevent multiple refreshes
        return []
    _is_refreshing = True
    raw = await repository.get_hottest_tags(db, limit=limit)
    hot_tags = [
            {"name": item["_id"], "blog_count": item["blog_count"]}
            for item in raw
        ]
    try:
        await redis_client.set(CACHE_KEY, json.dumps(hot_tags), ex=600)
    except Exception as e:
        logger.error(f"Failed to cache hottest tags: {e}")
    finally:
        _is_refreshing = False


    return [
        HottestTagResponse(
            tag=item["_id"],
            blog_count=item["blog_count"],
        )
        for item in raw
    ]


async def get_cached_hot_tags(limit: int = 10) -> List[HottestTagResponse]:
    data = await redis_client.get(CACHE_KEY)

    if data:
        return [
        HottestTagResponse(
            tag=item["name"],
            blog_count=item["blog_count"],
        )
        for item in json.loads(data)
    ]


    return []

# hottest view blog
async def list_hottest_blogs_by_views(limit: int = 10) -> List[BlogViewRankResponse]:
    items = await repository.list_blogs_by_views(db, limit=limit)
    return [BlogViewRankResponse(**item) for item in items]


async def like_blog(blog_id: str, user_id: str):

    blog = await repository.find_blog_by_id(db, blog_id)

    if not blog:
        raise HTTPException(status_code=404, detail="Blog post not found")

    liked_by_list = blog.get("liked_by", [])

    is_liked = True
    try:
        b_oid = ObjectId(blog_id)
        u_oid = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    like_num = 1
    if u_oid in liked_by_list:
        like_num *= -1
        is_liked = False
    success = await repository.modify_liked_by(db, blog_id, user_id, like_num)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update like status")

    updated_blog = await repository.find_blog_by_id(db, blog_id)
    like_count = updated_blog.get("like_count", 0)

    return {
        "is_liked": is_liked,
        "like_count": like_count
    }

