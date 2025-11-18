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


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete comment and its replies",
    description=(
        "Delete a comment and all its nested replies. "
        "Blog author can delete any comment under their blog. "
        "Comment author can delete their own comments."
    ),
)
async def delete_comment_endpoint(
    comment_id: str = Path(..., min_length=24, max_length=24, description="Comment ID (MongoDB ObjectId string)"),
    blog_id: str = Query(..., min_length=24, max_length=24, description="Blog ID this comment belongs to"),
    claims: dict = Depends(auth.verify_access_token),
):
    author_id = claims["sub"]
    logger.info(
        "Delete comment request, comment_id is %s, blog_id is %s, requester is %s",
        comment_id,
        blog_id,
        author_id,
    )
    await comment_service.remove_comment(comment_id=comment_id, blog_id=blog_id, author_id=author_id)
    logger.info("Deleted comment, comment_id is %s", comment_id)
    return None


@router.get(
    "/blog/{blog_id}",
    response_model=List[CommentResponse],
    status_code=status.HTTP_200_OK,
    summary="List comments for a blog",
    description=(
        "Fetch all comments and nested replies for a given blog. "
        "Returns a tree structure: top-level comments each with a replies list."
    ),
)
async def list_blog_comments_endpoint(
    blog_id: str = Path(..., min_length=24, max_length=24, description="Blog ID (MongoDB ObjectId string)"),
):
    logger.info("List comments for blog, blog_id is %s", blog_id)
    comments = await comment_service.get_comments_for_blog(blog_id)
    return comments

