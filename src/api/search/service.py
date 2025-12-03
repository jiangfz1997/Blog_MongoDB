from typing import List, Optional, Dict

from src.db.mongo import get_db
from src.api.users import repository as user_repository
from src.api.blogs import repository as blog_repository

from .schemas import (
    SearchUserPreview,
    SearchBlogPreview,
    BlogListPage,
    SearchUserResult,
    SearchBlogsResult, BlogSortField, SortDirection
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
    db = get_db()

    # Collect all author IDs (there may be multiple authors in keyword search results).
    author_ids = {doc["author_id"] for doc in blog_docs}

    # Batch query author usernames (to avoid repeated database lookups).
    # username_map: Dict[str, str] = {}
    # for uid in author_ids:
    #     user = await user_repository.find_by_id(db, uid)
    #     username_map[uid] = user["username"] if user else "Unknown"

    users = await user_repository.find_by_id_list(db, list(author_ids))
    users_map: Dict[str, Dict[str, str]] = {}

    for user in users:
        user_id = str(user.get("_id") or user.get("id"))
        users_map[user_id] = {
            "username": user["username"],
            "avatar_url": user.get("avatar_url", ""),
        }

    # Build blog preview list
    items: List[SearchBlogPreview] = []
    for doc in blog_docs:
        author_info = users_map.get(doc["author_id"])
        if not author_info:
            # Author not exist or inconsistent data
            author_username = "[deleted]"
            avatar_url = ""
        else:
            author_username = author_info["username"]
            avatar_url = author_info["avatar_url"]

        items.append(
            SearchBlogPreview(
                blog_id=doc["id"],
                title=doc["title"],
                author_username=author_username,
                avatar_url=avatar_url,
                created_at=doc["created_at"],
                updated_at=doc.get("updated_at"),
                tags=doc.get("tags", []),
                view_count=doc.get("view_count", 0),
                like_count=doc.get("like_count", 0),
                is_liked=doc.get("is_liked", False),
                comment_count=doc.get("comment_count", 0),
            )
        )

    return BlogListPage(
        total=total,
        page=page,
        size=size,
        items=items,
    )


async def search_user_with_blogs(username: str, page, size) -> SearchUserResult:
    """
    Search username:
    - If the user is found, return the user preview
    """
    db = get_db()

    user_doc = await user_repository.find_by_username(db, username)

    if not user_doc:
        return SearchUserResult(user=None)

    # user preview information
    user_preview = SearchUserPreview(username=user_doc["username"], user_id=str(user_doc["_id"]))

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
        # blogs=blogs_page,
    )


async def search_blogs_by_keyword(
        keyword: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 0,
        size: int = 10,
        sort_by: BlogSortField = BlogSortField.CREATED_AT,
        sort_order: SortDirection = SortDirection.DESC,
) -> SearchBlogsResult:
    """
    Search blog titles by keyword (case-insensitive).
    Return the paginated blog results.
    """
    db = get_db()
    skip = (page - 1) * size

    total = await blog_repository.count_blogs(db, keyword, tags)
    if total == 0:
        empty_page = BlogListPage(total=0, page=page, size=size, items=[])
        return SearchBlogsResult(blogs=empty_page)

    # current page
    blog_docs = await blog_repository.find_blogs_by_filters(
        db=db,
        keyword=keyword,
        tags=tags,
        skip=skip,
        limit=size,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    blogs_page = await _build_blog_list_page(
        blog_docs=blog_docs,
        total=total,
        page=page,
        size=size,
    )

    return SearchBlogsResult(blogs=blogs_page)


async def fetch_trending_blogs(user_id: str, page: int = 1, size: int = 5) -> SearchBlogsResult:
    LOOKBACK_DAYS = 100
    GRAVITY = 1.8
    db = get_db()

    recommended_blogs = await blog_repository.get_trending_feed(
        db,
        user_id,
        page=page,
        size=size,
        days_window=LOOKBACK_DAYS,
        gravity=GRAVITY
    )

    total = len(recommended_blogs)

    blogs_page = await _build_blog_list_page(
        blog_docs=recommended_blogs,
        total=total,
        page=page,
        size=size,
    )

    return SearchBlogsResult(blogs=blogs_page)


async def search_usernames_by_relevance(username: str, page: int = 1, limit: int = 10) -> List[SearchUserPreview]:
    """
    Search usernames by relevance using the repository function.
    """
    db = get_db()

    user_docs, total = await user_repository.search_users_by_relevance(db, username, page=page, limit=limit)
    user_docs_previews = [
        SearchUserPreview(
            username=doc["username"],
            user_id=str(doc["_id"]),
            avatar_url=doc.get("avatar_url", ""),
            bio=doc.get("bio", "")
        )
        for doc in user_docs
    ]
    return user_docs_previews, total
