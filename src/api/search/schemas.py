from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from enum import Enum


class SearchUserPreview(BaseModel):
    username: str = Field(..., description="Unique username of the user")
    user_id: str

class SearchBlogPreview(BaseModel):
    blog_id: str = Field(..., description="Public identifier of the blog (used for navigation)")
    title: str = Field(..., description="Title of the blog")
    author_username: str = Field(..., description="Username of the author")
    created_at: datetime = Field(..., description="When the blog was created")
    updated_at: Optional[datetime] = Field(None, description="When the blog was last updated")
    tags: Optional[List[str]] = Field(None, description="Tags associated with the blog")
    view_count: Optional[int] = Field(0, ge=0, description="Number of views")


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


class BlogSortField(str, Enum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    VIEWS_COUNT = "view_count"
    LIKE_COUNT = "like_count"
    COMMENTS_COUNT = "comment_count"

class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

class BlogSortQuery(str, Enum):
    CREATE_DATE = "created"
    UPDATE_DATE = "updated"
    VIEWS = "views"
    LIKES = "likes"
    COMMENTS = "comments"