from fastapi import APIRouter, HTTPException
from src.api.blogs.schemas import *
from src.logger import get_logger
from fastapi.encoders import jsonable_encoder

logger = get_logger()
router = APIRouter(
    prefix="/blogs",
    tags=["blogs"],
)
from bson import ObjectId
from src.auth.auth import create_access_token, create_refresh_token
from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
# src/api/blogs/router.py
from fastapi import APIRouter, Depends, status, Path, Query
from src.api.blogs import service
from src.auth import auth

router = APIRouter(prefix="/blogs", tags=["blogs"])

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
    logger.info("Created the blog, author_id is", author_id)
    return await service.create_blog(author_id, payload)

@router.patch(
    "/{blog_id}",
    response_model=BlogResponse,
    summary="Update blog",
    description="Partially update a blog's title/content. Only the author can update."
)
async def update_blog_endpoint(
    blog_id: str,
    payload: BlogUpdate,
    claims: dict = Depends(auth.verify_access_token),
):
    author_id = claims["sub"]
    update_fields = payload.dict(exclude_unset=True)
    logger.info("Updated the blog, blog_id is", blog_id)
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
    logger.info("Deleted the blog, blog_id is", blog_id)
    return None

#get blog by blog_id
@router.get(
    "/{blog_id}",
    response_model=BlogResponse,
    status_code=status.HTTP_200_OK,
    summary="Get blog by ID",
    description="Fetch a blog post by its ID."
)
async def get_blog_by_id_endpoint(
    blog_id: str = Path(..., min_length=24, max_length=24, description="MongoDB ObjectId string")
):
    logger.info("list the blog, blog_id is", blog_id)
    return await service.get_blog(blog_id)


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
    logger.info("list my blog, author_id is",author_id)
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
):
    logger.info("list others blog, author_id is", author_id)
    return await service.list_author_blogs(author_id, page, size)

