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
    根据博客文档构建分页返回模型：
    自动收集作者ID -> 批量查用户名 -> 转成 SearchBlogPreview 列表。
    """

    # 1. 收集所有作者ID（关键字搜索场景中会有多个作者）
    author_ids = {doc["author_id"] for doc in blog_docs}

    # 2. 批量查询作者用户名（避免重复查数据库）
    username_map: Dict[str, str] = {}
    for uid in author_ids:
        user = await user_repository.find_by_id(db, uid)
        username_map[uid] = user["username"] if user else "Unknown"

    # 3. 构建博客预览列表
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

    # 4. 拼装分页结构
    return BlogListPage(
        total=total,
        page=page,
        size=size,
        items=items,
    )

async def search_user_with_blogs(username: str,) -> SearchUserResult:
    """
    搜索用户名：
    - 如果找到该用户，返回用户预览
    """

    user_doc = await user_repository.find_by_username(db, username)

    if not user_doc:
        # 用户名不存在
        return SearchUserResult(user=None)

    # 用户预览信息
    user_preview = SearchUserPreview(username=user_doc["username"],user_id=str(user_doc["_id"]))

    # # 查询该用户的博客
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
    按关键字搜索博客标题（不区分大小写）。
    返回分页后的博客结果。
    """
    skip = (page - 1) * size

    # 1. 总数
    total = await blog_repository.count_blogs_by_title(db, keyword)
    if total == 0:
        empty_page = BlogListPage(total=0, page=page, size=size, items=[])
        return SearchBlogsResult(blogs=empty_page)

    # 2. 当前页数据
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