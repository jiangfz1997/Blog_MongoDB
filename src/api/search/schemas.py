from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SearchUserPreview(BaseModel):
    username: str = Field(..., description="Unique username of the user")
    user_id: str

class SearchBlogPreview(BaseModel):
    blog_id: str = Field(..., description="Public identifier of the blog (used for navigation)")
    title: str = Field(..., description="Title of the blog")
    author_username: str = Field(..., description="Username of the author")
    created_at: datetime = Field(..., description="When the blog was created")


class BlogListPage(BaseModel):
    """
    total: total number of matching items
    page: current page number, starting from 1
    size: number of items per page
    items: list of blog previews for the current page
    """
    total: int = Field(..., ge=0, description="Total number of matched blogs")
    page: int = Field(..., ge=1, description="Current page number (1-based)")
    size: int = Field(..., ge=1, description="Page size")
    items: List[SearchBlogPreview]

# search username
class SearchUserResult(BaseModel):
    user: Optional[SearchUserPreview] = None


#search keyword
class SearchBlogsResult(BaseModel):
    blogs: BlogListPage