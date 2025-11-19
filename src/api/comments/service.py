import asyncio
from datetime import datetime
from src.db.mongo import db
from src.api.comments import repository as comment_repository
from src.api.comments.schemas import *
from fastapi import HTTPException, status
from src.api.blogs import repository as blog_repository
from src.api.users import repository as user_repository
from src.api.users import service as user_service
from typing import List, Dict, Any

from src.logger import get_logger

logger = get_logger()



# ---------------------------
# 创建评论（root / reply）
# ---------------------------
async def create_comment(author_id: str, comment_in: CommentCreate) -> CommentResponse:
    """
    创建评论（root 或 reply）。
    - root：parent_id = None
    - reply：parent_id = 某条已有评论的 id
    这里会：
      1. 处理 is_root / root_id / reply_to_comment_id / reply_to_username
      2. 查询作者 username，填充 author_username
      3. 返回 CommentResponse（满足 router 的 response_model 要求）
    """

    # 1. blog 必须存在
    blog = await blog_repository.find_blog_by_id(db, comment_in.blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    # 2. 根据 parent_id 判定 root / reply
    if comment_in.parent_id is None:
        # 根评论
        is_root = True
        root_id = None
        reply_to_comment_id = None
        reply_to_username = None
    else:
        # 回复评论，先确保 parent 存在
        parent = await comment_repository.find_comment_by_id(db, comment_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment not found",
            )

        is_root = False
        root_id = parent["root_id"]
        reply_to_comment_id = comment_in.parent_id

        # 方案2：创建时就把被回复者用户名快照下来
        #parent_user = await user_repository.find_by_id(db, parent["author_id"])
        parent_user = await user_service.get_user_public(parent["author_id"])
        if not parent_user:
            reply_to_username = "Unknown"
        else:
            reply_to_username = parent_user.username

    # 3. 写入数据库的文档
    comment_doc = {
        "content": comment_in.content,
        "blog_id": comment_in.blog_id,
        "author_id": author_id,
        "created_at": datetime.utcnow(),
        "is_root": is_root,
        "root_id": root_id,
        "parent_id": comment_in.parent_id,
        "reply_to_comment_id": reply_to_comment_id,
        "reply_to_username": reply_to_username,
    }

    created = await asyncio.wait_for(
        comment_repository.add_comment(db, comment_doc),
        timeout=5,
    )

    # root 评论：如果 root_id 仍是 None，则补成自己的 id
    if created["is_root"] and created["root_id"] is None:
        created["root_id"] = created["id"]

    # 4. 这里是关键：查当前作者 username，补上 author_username
    #user = await user_repository.find_by_id(db, author_id)
    user = await user_service.get_user_public(author_id)
    author_username = user.username if user else "Unknown"

    # 5. 返回一个完整的 CommentResponse
    return CommentResponse(
        **created,
        author_username=author_username,
    )


# ---------------------------
# 删除评论
# ---------------------------
async def remove_comment(comment_id: str, blog_id: str, author_id: str) -> None:
    """
    新规则下的删除逻辑：
      - root 评论：删除整条 thread（delete_root_thread）
      - reply：仅删除该条（delete_single_comment）

    权限规则：
      - 博客作者可以删除该博客下的任何评论
      - 评论作者只能删除自己的评论
    """

    # 1. 评论必须存在
    existing = await comment_repository.find_comment_by_id(db, comment_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # 2. 确保评论属于该 blog（避免越权）
    if existing["blog_id"] != blog_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the blog",
        )

    # 3. blog 必须存在
    blog = await blog_repository.find_blog_by_id(db, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    # 4. Permission check：博客作者 OR 评论作者
    if blog["author_id"] != author_id and existing["author_id"] != author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    # ---------------------------
    # 删除逻辑
    # ---------------------------
    if existing["is_root"]:
        # 删除整条 root thread
        deleted_count = await comment_repository.delete_root_thread(db, existing["id"])
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Delete failed",
            )
    else:
        #删除单条 reply
        ok = await comment_repository.delete_single_comment(db, comment_id)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Delete failed",
            )


# ---------------------------
# 获取某篇 blog 的评论（root 分页 + 每条 root 的 reply 分页）
# ---------------------------
async def get_comments_for_blog(
    blog_id: str,
    page: int,
    size: int,
    replies_page: int = 1,
    replies_size: int = 10,
) -> CommentListResponse:
    """
    获取某篇博客的 root 评论分页，并为每个 root 带上一页 replies。
    """

    # 1. blog 必须存在
    blog = await blog_repository.find_blog_by_id(db, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    # 2. root 分页
    skip = (page - 1) * size
    root_comments = await comment_repository.list_root_comments_by_blog(
        db, blog_id, skip=skip, limit=size
    )
    total = await comment_repository.count_root_comments_by_blog(db, blog_id)

    if not root_comments:
        return CommentListResponse(
            items=[],
            page=page,
            size=size,
            total=0,
            has_next=False,
        )

    # 3. 批量收集所有需要的 author_id，用于查 author_username
    author_ids = {c["author_id"] for c in root_comments}
    root_ids = [c["id"] for c in root_comments]

    # 每个 root 对应的 replies 首页和总数
    all_replies_per_root: Dict[str, List[dict]] = {}
    all_reply_totals: Dict[str, int] = {}

    for rid in root_ids:
        rskip = (replies_page - 1) * replies_size
        replies = await comment_repository.list_replies_by_root(
            db, rid, skip=rskip, limit=replies_size
        )
        rtotal = await comment_repository.count_replies_by_root(db, rid)

        all_replies_per_root[rid] = replies
        all_reply_totals[rid] = rtotal

        # 收集 replies 的作者 id
        for rp in replies:
            author_ids.add(rp["author_id"])
    logger.info("list author_ids=%s", author_ids)
    # 4. 一次性查出所有作者的用户名
    id_to_username={}
    for i in author_ids:
        #users = await user_repository.find_by_id(db, i)
        users = await user_service.get_user_public(i)
        logger.info("users=%s", users)
        id_to_username[i]=users.username
    logger.info("id_to_username=%s", id_to_username)
    #id_to_username = {u["id"]: u["username"] for u in users}

    # 5. 组装 RootCommentResponse 列表
    root_responses: List[RootCommentResponse] = []

    for root in root_comments:
        root_author_username = id_to_username.get(root["author_id"], "Unknown")

        replies_docs = all_replies_per_root[root["id"]]
        formatted_replies: List[CommentResponse] = []

        for rp in replies_docs:
            reply_author_username = id_to_username.get(rp["author_id"], "Unknown")

            # 方案 2：直接使用文档中的 reply_to_username 快照
            reply_to_username = rp.get("reply_to_username")

            formatted_replies.append(
                CommentResponse(
                    **rp,
                    author_username=reply_author_username,
                    #reply_to_username=reply_to_username,
                )
            )

        root_responses.append(
            RootCommentResponse(
                **root,
                author_username=root_author_username,
                replies=formatted_replies,
                replies_page=replies_page,
                replies_size=replies_size,
                replies_total=all_reply_totals[root["id"]],
                replies_has_next=(replies_page * replies_size < all_reply_totals[root["id"]]),
            )
        )

    return CommentListResponse(
        items=root_responses,
        page=page,
        size=size,
        total=total,
        has_next=(page * size < total),
    )
