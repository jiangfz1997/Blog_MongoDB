import asyncio
from datetime import datetime
from src.db.mongo import db
from src.api.comments import repository as comment_repository
from src.api.comments.schemas import CommentCreate, CommentResponse
from fastapi import HTTPException, status
from src.api.blogs import repository as blog_repository
from typing import List

async def create_comment(author_id: str, comment_in: CommentCreate) -> dict:
    """
    create comment
    """
    # check blog
    blog = await blog_repository.find_blog_by_id(db, comment_in.blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    comment_doc = {
        "content": comment_in.content,
        "blog_id": comment_in.blog_id,
        "author_id": author_id,             # JWT
        "parent_id": comment_in.parent_id,
        "created_at": datetime.utcnow(),
    }

    created = await asyncio.wait_for(
        comment_repository.add_comment(db, comment_doc),
        timeout=5,
    )
    return created


async def remove_comment(comment_id: str, blog_id: str, author_id: str) -> None:
    """
    删除一条评论及其所有子孙回复。

    权限规则：
    - 博客作者可以删除自己博客下的任意评论
    - 评论作者可以删除自己的评论（无论在哪个博客下）
    """
    # 1. 先确保评论存在
    existing = await comment_repository.find_comment_by_id(db, comment_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # 2. 确保这条评论确实属于这篇博客
    if existing["blog_id"] != blog_id:
        # 你也可以选择返回 404，防止暴露信息
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to this blog",
        )

    # 3. 检查博客是否存在
    blog = await blog_repository.find_blog_by_id(db, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    # 4. 权限检查：博客作者 或 评论作者 才能删
    if blog["author_id"] != author_id and existing["author_id"] != author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    # 5. 级联删除这条评论以及其所有子孙评论
    ok = await asyncio.wait_for(
        comment_repository.delete_comment_tree(db, comment_id),
        timeout=5,
    )
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Delete failed",
        )

async def get_comments_for_blog(blog_id: str) -> List[CommentResponse]:
    """
    获取某篇博客下的所有评论，并组装成楼中楼结构。
    返回一个 CommentResponse 的列表（顶层评论），每个都带 replies。
    """

    # 可选：检查博客是否存在
    blog = await blog_repository.find_blog_by_id(db, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    # 从仓库拿到平铺的评论列表（每一项是 dict）
    flat_comments = await comment_repository.list_comments_by_blog(db, blog_id)
    if not flat_comments:
        return []

    # 先把每条评论包装成 dict 节点，并准备好 replies = []
    # 注意：这里先用 dict，FastAPI 最后会用 CommentResponse 自动做转换
    id_to_node: dict[str, dict] = {}
    roots: List[dict] = []

    for c in flat_comments:
        node = {
            "id": c["id"],
            "blog_id": c["blog_id"],
            "author_id": c["author_id"],
            "parent_id": c["parent_id"],
            "content": c["content"],
            "created_at": c["created_at"],
            "replies": [],  # 初始化为空列表，方便 append
        }
        id_to_node[node["id"]] = node

    # 第二轮：根据 parent_id 挂到父节点的 replies 下面
    for node in id_to_node.values():
        parent_id = node["parent_id"]
        if parent_id and parent_id in id_to_node:
            id_to_node[parent_id]["replies"].append(node)
        else:
            # 没有 parent_id，或者 parent 不在本次结果中 → 顶层评论
            roots.append(node)

    # 最后把 dict 列表交给 Pydantic 转成 CommentResponse 模型
    return [CommentResponse(**root) for root in roots]