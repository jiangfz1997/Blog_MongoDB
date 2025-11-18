import asyncio
from datetime import datetime
from src.db.mongo import db
from . import repository
from src.api.blogs.schemas import *
from fastapi import HTTPException, status
from typing import Dict, Any, Optional

async def create_blog(author_id: str, blog_in: BlogCreate) -> dict:
    blog_doc = {
        "title": blog_in.title,
        "content": blog_in.content,
        "author_id": author_id,                 # from JWT
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "tags": blog_in.tags,
    }
    created = await asyncio.wait_for(repository.add_blog(db, blog_doc), timeout=5)
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
async def get_blog(blog_id: str) -> dict:
    doc = await repository.find_blog_by_id_and_inc_view(db, blog_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
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
async def list_author_blogs(author_id: str, page: int = 1, size: int = 10) -> Dict[str, Any]:
    page = max(page, 1)
    size = max(min(size, 50), 1)
    skip = (page - 1) * size

    items = await repository.list_blogs_by_author(db, author_id, limit=size, skip=skip)
    total = await repository.count_blogs_by_author(db, author_id)
    return {
        "items": items,
        "page": page,
        "size": size,
        "total": total,
        "has_next": page * size < total,
    }

# hottest blog tag
async def get_hottest_tags(limit: int = 10) -> List[HottestTagResponse]:
    """
    Service: 获取当前最热的标签排行榜。
    依据：拥有该标签的博客数量，从高到低排序。
    """
    raw = await repository.get_hottest_tags(db, limit=limit)
    return [
        HottestTagResponse(
            tag=item["_id"],
            blog_count=item["blog_count"],
        )
        for item in raw
    ]

# hottest view blog
async def list_hottest_blogs_by_views(limit: int = 10) -> List[BlogViewRankResponse]:
    items = await repository.list_blogs_by_views(db, limit=limit)
    return [BlogViewRankResponse(**item) for item in items]