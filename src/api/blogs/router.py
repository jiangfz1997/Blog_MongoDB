from fastapi import APIRouter, BackgroundTasks, HTTPException
from src.api.blogs.schemas import *
from src.logger import get_logger

logger = get_logger()
router = APIRouter(
    prefix="/blogs",
    tags=["blogs"],
)

from fastapi import APIRouter, Depends, status, Path, Query
from src.api.blogs import service
from src.auth import auth

@router.post(
    "",
    response_model=BlogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create blog",
    description="Create a new blog post. Requires login."
)
async def create_blog_endpoint(
    payload: BlogCreate,
    claims: dict = Depends(auth.verify_access_token),
):
    author_id = claims["sub"]
    logger.debug("Created the blog, author_id is=%s", author_id)
    return await service.create_blog(author_id, payload)

@router.patch(
    "/{blog_id}",
    response_model=BlogResponse,
    summary="Update blog",
    description="Partially update a blog. Only the author can update."
)
async def update_blog_endpoint(
    blog_id: str,
    payload: BlogUpdate,
    claims: dict = Depends(auth.verify_access_token),
):
    author_id = claims["sub"]
    update_fields = payload.dict(exclude_unset=True)
    logger.debug("Updated the blog, blog_id is=%s", blog_id)
    return await service.edit_blog(blog_id, author_id, update_fields)

@router.delete(
    "/{blog_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete blog",
    description="Delete a blog by ID. Only the author can delete."
)
async def delete_blog_endpoint(
    blog_id: str,
    claims: dict = Depends(auth.verify_access_token),
):
    author_id = claims["sub"]
    await service.remove_blog(blog_id, author_id)
    logger.debug("Deleted the blog, blog_id is=%s", blog_id)
    return None

#get blog by blog_id
@router.get(
    "/{blog_id}",
    response_model=BlogResponse,
    status_code=status.HTTP_200_OK,
    summary="Get blog by ID",
    description="Fetch a blog post by its ID.",
)
async def get_blog_by_id_endpoint(
    blog_id: str = Path(..., min_length=24, max_length=24, description="MongoDB ObjectId string"),
    current_user: dict | None = Depends(auth.try_get_current_user)
):
    logger.debug("list the blog, blog_id is=%s", blog_id)
    user_id = current_user["id"] if current_user else None
    return await service.get_blog(blog_id, user_id)

@router.get(
    "/{blog_id}/preview",
    response_model=BlogPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Get blog preview by ID",
    description="Fetch blog meta info (without content) by blog ID.",
)
async def get_blog_preview_endpoint(
    blog_id: str = Path(..., min_length=24, max_length=24, description="MongoDB ObjectId string"),
):
    logger.debug("get blog preview, blog_id is %s", blog_id)
    return await service.get_blog_preview(blog_id)


# get my blog
@router.get(
    "/author/me",
    summary="List my blogs",
    description="List blogs written by the current user, newest first."
)
async def list_my_blogs_endpoint(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    claims: dict = Depends(auth.verify_access_token),
):
    author_id = claims["sub"]
    logger.debug("list my blog, author_id is=%s",author_id)
    return await service.list_author_blogs(author_id, page, size)

#get other people blog
@router.get(
    "/author/{author_id}",
    summary="List blogs by author",
    description="List blogs written by the specified author, newest first."
)
async def list_blogs_by_author_endpoint(
    author_id: str = Path(..., description="User ID of the author"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    exclude_blog_id: Optional[str] = Query(None, description="Blog ID to exclude from results")
):
    logger.debug("list others blog, author_id is=%s", author_id)
    return await service.list_author_blogs(author_id, page, size, exclude_blog_id)

# hottest blog tag
@router.get(
    "/tags/hottest",
    response_model=List[HottestTagResponse],
    status_code=status.HTTP_200_OK,
    summary="Get hottest tags",
    description="Get the hottest tags ranked by the number of blogs having each tag.",
)
async def get_hottest_tags_endpoint(
    # background_tasks: BackgroundTasks,
    limit: int = Query(10, ge=1, le=50, description="Maximum number of tags to return"),
):
    tags = await service.get_cached_hot_tags(limit)
    if tags:
        return tags
    # background_tasks.add_task(service.get_hottest_tags, limit)
    return []
# hottest view count blog
@router.get(
    "/views/hottest",
    response_model=List[BlogViewRankResponse],
    status_code=status.HTTP_200_OK,
    summary="Get blogs ranked by view count",
    description="Get the list of blogs with highest view counts, in descending order.",
)
async def get_hottest_blogs_by_views_endpoint(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of blogs to return"),
):
    return await service.list_hottest_blogs_by_views(limit)

@router.post(
    "/{blog_id}/like",
    response_model=BlogLikeResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle like on a blog",
    description="Toggle like status (Like/Unlike). Requires login."
)
async def like_blog_post(
    blog_id: str = Path(..., min_length=24, max_length=24, description="MongoDB ObjectId string"),
    claims: dict = Depends(auth.verify_access_token),
):
    user_id = claims["sub"]
    logger.debug("User %s liked blog %s", user_id, blog_id)
    return await service.like_blog(blog_id, user_id)

