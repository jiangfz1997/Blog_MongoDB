from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class SearchUserPreview(BaseModel):
    username: str = Field(..., description="Unique username of the user")

class SearchBlogPreview(BaseModel):
    blog_id: str = Field(..., description="Public identifier of the blog (used for navigation)")
    title: str = Field(..., description="Title of the blog")
    author_username: str = Field(..., description="Username of the author")
    created_at: datetime = Field(..., description="When the blog was created")


class BlogListPage(BaseModel):
    """
    通用博客分页结构：
    - total: 符合条件的总条数
    - page: 当前页码，从 1 开始
    - size: 每页条数
    - items: 当前页的博客预览列表
    """
    total: int = Field(..., ge=0, description="Total number of matched blogs")
    page: int = Field(..., ge=1, description="Current page number (1-based)")
    size: int = Field(..., ge=1, description="Page size")
    items: List[SearchBlogPreview]

# search username
class SearchUserResult(BaseModel):
    user: Optional[SearchUserPreview] = None
    blogs: BlogListPage

#search keyword
class SearchBlogsResult(BaseModel):
    blogs: BlogListPage