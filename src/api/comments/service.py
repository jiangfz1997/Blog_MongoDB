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



async def create_comment(author_id: str, comment_in: CommentCreate) -> CommentResponse:
    """
    Create a comment (root or reply).
    Root: parent_id = None
    Reply: parent_id = the id of an existing comment

    This function will:
    Set is_root / root_id / reply_to_comment_id / reply_to_username
    Look up the author's username and fill author_username
    Return CommentResponse (to satisfy the router's response_model)
    """

    # make sure blog exists
    blog = await blog_repository.find_blog_by_id(db, comment_in.blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    # Determine whether it is a root comment or a reply based on parent_id.
    if comment_in.parent_id is None:
        # root comment
        is_root = True
        root_id = None
        reply_to_comment_id = None
        reply_to_username = None
    else:
        # Reply to a comment, ensuring the parent comment exists first.
        parent = await comment_repository.find_comment_by_id(db, comment_in.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment not found",
            )

        is_root = False
        root_id = parent["root_id"]
        reply_to_comment_id = comment_in.parent_id

        #parent_user = await user_repository.find_by_id(db, parent["author_id"])
        parent_user = await user_service.get_user_public(parent["author_id"])
        if not parent_user:
            reply_to_username = "Unknown"
        else:
            reply_to_username = parent_user.username

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

    # Root comment: if root_id is None, set it to its own id.
    if created["is_root"] and created["root_id"] is None:
        created["root_id"] = created["id"]

    # fetch the author's username and populate author_username.
    #user = await user_repository.find_by_id(db, author_id)
    user = await user_service.get_user_public(author_id)
    author_username = user.username if user else "Unknown"

    return CommentResponse(
        **created,
        author_username=author_username,
    )



async def remove_comment(comment_id: str, blog_id: str, author_id: str) -> None:
    """
    Root comment: delete the entire thread (delete_root_thread)
    Reply: delete only that single comment (delete_single_comment)

    Permission rules:
    - The blog author can delete any comment under the blog
    - A comment author can delete only their own comment
    """

    # make sure comment/reply exists
    existing = await comment_repository.find_comment_by_id(db, comment_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # the comment belongs to the specified blog (to prevent unauthorized access)
    if existing["blog_id"] != blog_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the blog",
        )

    # make sure blog exists
    blog = await blog_repository.find_blog_by_id(db, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )

    # user permission check
    if blog["author_id"] != author_id and existing["author_id"] != author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )


    if existing["is_root"]:
        # delete whole root thread
        deleted_count = await comment_repository.delete_root_thread(db, existing["id"])
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Delete failed",
            )
    else:
        #delete single reply
        ok = await comment_repository.delete_single_comment(db, comment_id)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Delete failed",
            )



async def get_comments_for_blog(
    blog_id: str,
    page: int,
    size: int,
    replies_page: int = 1,
    replies_size: int = 10,
) -> CommentListResponse:
    """
    Get paginated root comments for a blog, with one page of replies attached to each root comment.
    """
    # ensure blog exists
    blog = await blog_repository.find_blog_by_id(db, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found",
        )


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

    # Collect all required author_id values in batch for querying author_username.
    author_ids = {c["author_id"] for c in root_comments}
    root_ids = [c["id"] for c in root_comments]

    # The first page of replies and the total reply count for each root comment.
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

        # collect author_id of replies
        for rp in replies:
            author_ids.add(rp["author_id"])
    logger.info("list author_ids=%s", author_ids)

    # Query all authors' usernames in a single batch
    id_to_username={}
    for i in author_ids:
        #users = await user_repository.find_by_id(db, i)
        users = await user_service.get_user_public(i)
        logger.info("users=%s", users)
        id_to_username[i]=users.username
    logger.info("id_to_username=%s", id_to_username)
    #id_to_username = {u["id"]: u["username"] for u in users}


    root_responses: List[RootCommentResponse] = []

    for root in root_comments:
        root_author_username = id_to_username.get(root["author_id"], "Unknown")

        replies_docs = all_replies_per_root[root["id"]]
        formatted_replies: List[CommentResponse] = []

        for rp in replies_docs:
            reply_author_username = id_to_username.get(rp["author_id"], "Unknown")


            formatted_replies.append(
                CommentResponse(
                    **rp,
                    author_username=reply_author_username,
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

# get replies list of oen specific root comment
async def get_replies_for_root(root_id: str, page: int, size: int) -> ReplyListResponse:

    root = await comment_repository.find_comment_by_id(db, root_id)
    if not root:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Root comment not found",
        )

    if not root.get("is_root", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The given comment is not a root comment",
        )

    page = max(page, 1)
    size = max(min(size, 50), 1)
    skip = (page - 1) * size

    replies = await comment_repository.list_replies_by_root(
        db, root_id, skip=skip, limit=size
    )
    total = await comment_repository.count_replies_by_root(db, root_id)

    if not replies:
        return ReplyListResponse(
            items=[],
            page=page,
            size=size,
            total=0,
            has_next=False,
        )

    author_ids = {rp["author_id"] for rp in replies}
    id_to_username = {}
    for i in author_ids:
        users = await user_service.get_user_public(i)
        id_to_username[i] = users.username
    logger.info("id_to_username=%s", id_to_username)


    formatted_replies: List[CommentResponse] = []
    for rp in replies:
        reply_author_username = id_to_username.get(rp["author_id"], "Unknown")
        formatted_replies.append(
            CommentResponse(
                **rp,
                author_username=reply_author_username,
            )
        )

    return ReplyListResponse(
        items=formatted_replies,
        page=page,
        size=size,
        total=total,
        has_next=(page * size < total),
    )