from typing import List, Optional, Dict

from src.db.mongo import db
from src.api.users import repository as user_repository
from src.api.blogs import repository as blog_repository

from .schemas import (
    SearchUserPreview,
    SearchBlogPreview,
    BlogListPage,
    SearchUserResult,
    SearchBlogsResult
)

async def _build_blog_list_page(
    blog_docs: List[dict],
    total: int,
    page: int,
    size: int,
) -> BlogListPage:
    """
    Build the paginated response model from blog documents:
    auto-collect author IDs -> batch query usernames -> convert to a list of SearchBlogPreview.
    """

    # Collect all author IDs (there may be multiple authors in keyword search results).
    author_ids = {doc["author_id"] for doc in blog_docs}

    # Batch query author usernames (to avoid repeated database lookups).
    username_map: Dict[str, str] = {}
    for uid in author_ids:
        user = await user_repository.find_by_id(db, uid)
        username_map[uid] = user["username"] if user else "Unknown"

    # Build blog preview list
    items: List[SearchBlogPreview] = []
    for doc in blog_docs:
        items.append(
            SearchBlogPreview(
                blog_id=doc["id"],
                title=doc["title"],
                author_username=username_map[doc["author_id"]],
                created_at=doc["created_at"],
            )
        )

    return BlogListPage(
        total=total,
        page=page,
        size=size,
        items=items,
    )

async def search_user_with_blogs(username: str,) -> SearchUserResult:
    """
    Search username:
    - If the user is found, return the user preview
    """

    user_doc = await user_repository.find_by_username(db, username)

    if not user_doc:
        return SearchUserResult(user=None)

    # user preview information
    user_preview = SearchUserPreview(username=user_doc["username"],user_id=str(user_doc["_id"]))

    # #author_id = user_doc["id"]
    # author_id = str(user_doc["_id"])
    # skip = (page - 1) * size
    #
    # total = await blog_repository.count_blogs_by_author(db, author_id)
    # if total == 0:
    #     empty_page = BlogListPage(total=0, page=page, size=size, items=[])
    #     return SearchUserResult(user=user_preview, blogs=empty_page)
    #
    # blog_docs = await blog_repository.list_blogs_by_author(
    #     db=db,
    #     author_id=author_id,
    #     limit=size,
    #     skip=skip,
    # )
    #
    # blogs_page = await _build_blog_list_page(
    #     blog_docs=blog_docs,
    #     total=total,
    #     page=page,
    #     size=size,
    # )

    return SearchUserResult(
        user=user_preview,
        #blogs=blogs_page,
    )


async def search_blogs_by_keyword(
    keyword: str,
    page: int,
    size: int,
) -> SearchBlogsResult:
    """
    Search blog titles by keyword (case-insensitive).
    Return the paginated blog results.
    """
    skip = (page - 1) * size

    total = await blog_repository.count_blogs_by_title(db, keyword)
    if total == 0:
        empty_page = BlogListPage(total=0, page=page, size=size, items=[])
        return SearchBlogsResult(blogs=empty_page)

    # current page
    blog_docs = await blog_repository.search_blogs_by_title(
        db=db,
        keyword=keyword,
        skip=skip,
        limit=size,
    )

    blogs_page = await _build_blog_list_page(
        blog_docs=blog_docs,
        total=total,
        page=page,
        size=size,
    )

    return SearchBlogsResult(blogs=blogs_page)