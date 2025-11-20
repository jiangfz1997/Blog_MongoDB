from fastapi import APIRouter, HTTPException
from src.api.comments.schemas import *
from src.logger import get_logger

logger = get_logger()
router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)
from fastapi import APIRouter, Depends, status, Path, Query
from src.api.comments import service as comment_service
from src.auth import auth

@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create comment or reply",
    description=(
        "Create a new top-level comment or reply under a blog. "
        "Requires login. "
        "Set parent_id to null for top-level comments, "
        "or to an existing comment ID to create a reply."
    ),
)
async def create_comment_endpoint(
    payload: CommentCreate,
    claims: dict = Depends(auth.verify_access_token),
):
    author_id = claims["sub"]
    logger.info("Create comment, author_id is %s, blog_id is %s", author_id, payload.blog_id)
    created = await comment_service.create_comment(author_id, payload)
    return created

# delete comments
@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete comment",
    description=(
        "Delete a comment. "
        "If the comment is a top-level comment, the entire thread is deleted. "
        "If it is a reply, only that reply is deleted. "
        "Blog author can delete any comment, "
        "and comment author can delete their own comments."
    ),
)
async def delete_comment_endpoint(
    comment_id: str = Path(..., min_length=24, max_length=24),
    blog_id: str = Query(..., min_length=24, max_length=24),
    claims: dict = Depends(auth.verify_access_token),
):
    author_id = claims["sub"]
    logger.info(
        "Delete comment request, comment_id=%s, blog_id=%s, requester=%s",
        comment_id,
        blog_id,
        author_id,
    )
    await comment_service.remove_comment(
        comment_id=comment_id,
        blog_id=blog_id,
        author_id=author_id,
    )
    logger.info("Deleted comment, comment_id=%s", comment_id)
    return None



# get comments and replies
@router.get(
    "/blog/{blog_id}",
    response_model=CommentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List comments for a blog (paginated)",
    description=(
        "List top-level comments with pagination, "
        "each including one page of replies. "
        "Use page/size for top-level comments, "
        "and replies_page/replies_size for replies pagination."
    ),
)
async def list_blog_comments_endpoint(
    blog_id: str = Path(..., min_length=24, max_length=24),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    replies_page: int = Query(1, ge=1),
    replies_size: int = Query(5, ge=1, le=50),
):
    logger.info(
        "List comments for blog, blog_id=%s (page=%s,size=%s,replies_page=%s,replies_size=%s)",
        blog_id, page, size, replies_page, replies_size,
    )

    comments = await comment_service.get_comments_for_blog(
        blog_id=blog_id,
        page=page,
        size=size,
        replies_page=replies_page,
        replies_size=replies_size,
    )
    return comments

# get replies list of specific root comment
@router.get(
    "/root/{root_id}/replies",
    response_model=ReplyListResponse,
    status_code=status.HTTP_200_OK,
    summary="List replies for a root comment (paginated)",
    description=(
        "Fetch paginated replies under a specific root comment. "
        "Use this endpoint when clicking 'Load more replies' "
        "for a particular root comment."
    ),
)
async def list_replies_for_root_endpoint(
    root_id: str = Path(..., min_length=24, max_length=24, description="Root comment ID"),
    page: int = Query(1, ge=1, description="Replies page number (1-based)"),
    size: int = Query(5, ge=1, le=50, description="Replies per page"),
):
    logger.info(
        "List replies for root comment, root_id=%s (page=%s,size=%s)",
        root_id,
        page,
        size,
    )
    return await comment_service.get_replies_for_root(root_id=root_id, page=page, size=size)




# @router.delete(
#     "/{comment_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     summary="Delete comment and its replies",
#     description=(
#         "Delete a comment and all its nested replies. "
#         "Blog author can delete any comment under their blog. "
#         "Comment author can delete their own comments."
#     ),
# )
# async def delete_comment_endpoint(
#     comment_id: str = Path(..., min_length=24, max_length=24, description="Comment ID (MongoDB ObjectId string)"),
#     blog_id: str = Query(..., min_length=24, max_length=24, description="Blog ID this comment belongs to"),
#     claims: dict = Depends(auth.verify_access_token),
# ):
#     author_id = claims["sub"]
#     logger.info(
#         "Delete comment request, comment_id is %s, blog_id is %s, requester is %s",
#         comment_id,
#         blog_id,
#         author_id,
#     )
#     await comment_service.remove_comment(comment_id=comment_id, blog_id=blog_id, author_id=author_id)
#     logger.info("Deleted comment, comment_id is %s", comment_id)
#     return None
#
#
# @router.get(
#     "/blog/{blog_id}",
#     response_model=List[CommentResponse],
#     status_code=status.HTTP_200_OK,
#     summary="List comments for a blog",
#     description=(
#         "Fetch all comments and nested replies for a given blog. "
#         "Returns a tree structure: top-level comments each with a replies list."
#     ),
# )
# async def list_blog_comments_endpoint(
#     blog_id: str = Path(..., min_length=24, max_length=24, description="Blog ID (MongoDB ObjectId string)"),
# ):
#     logger.info("List comments for blog, blog_id is %s", blog_id)
#     comments = await comment_service.get_comments_for_blog(blog_id)
#     return comments

