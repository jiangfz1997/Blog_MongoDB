from pydantic import BaseModel, Field,field_validator
from datetime import datetime
from typing import Optional, List


MAX_TAGS_PER_BLOG = 6
# blog creation
class BlogCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=30, description="Blog title between 3 and 30 characters")
    content: str = Field(..., min_length=10, description="Blog content, at least 10 characters")
    # tags: conlist(str, max_items=MAX_TAGS_PER_BLOG) = Field(default_factory=list,description="User-defined tags, at most 6 per blog")
    tags: List[str] = Field(default_factory=list, description="User-defined tags, at most 6 per blog")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        v = [tag.strip() for tag in v if tag.strip()]
        v = list(dict.fromkeys(v))
        if len(v) > MAX_TAGS_PER_BLOG:
            raise ValueError(f"At most {MAX_TAGS_PER_BLOG} tags are allowed.")
        return v



# blog update
class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=30)
    content: Optional[str] = Field(None, min_length=10)
    tags: Optional[List[str]] = Field(None, description="Optional user-defined tags, at most 6 per blog")

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        v = [tag.strip() for tag in v if tag.strip()]
        v = list(dict.fromkeys(v))
        if len(v) > MAX_TAGS_PER_BLOG:
            raise ValueError(f"At most {MAX_TAGS_PER_BLOG} tags are allowed.")
        return v


# blog delete
class BlogDelete(BaseModel):
    blog_id: str = Field(..., description="ID of the blog to delete")


# blog response
class BlogResponse(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    author_username: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list, description="User-defined tags of the blog")
    view_count: int = Field(0, ge=0, description="Total view count of the blog")
    like_count: int = Field(0, ge=0, description="Total like count of the blog")
    is_liked: bool = Field(False, description="Whether the current user has liked the blog, False for unauthenticated users")

class BlogPreviewResponse(BaseModel):
    id: str = Field(..., description="Blog ID")
    title: str = Field(..., description="Blog title")
    author_id: str = Field(..., description="Author user ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime | None = Field(None, description="Last update time")
    tags: List[str] = Field(default_factory=list, description="User-defined tags of the blog")
    view_count: int = Field(0, ge=0, description="Total view count of the blog")


class HottestTagResponse(BaseModel):
    tag: str = Field(..., description="Tag name")
    blog_count: int = Field(..., ge=1, description="Number of blogs having this tag")

class BlogViewRankResponse(BaseModel):
    id: str = Field(..., description="Blog ID")
    title: str = Field(..., description="Blog title")
    author_id: str = Field(..., description="Author user ID")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime | None = Field(None, description="Last update time")
    tags: List[str] = Field(default_factory=list, description="User-defined tags of the blog")
    view_count: int = Field(..., ge=0, description="Total view count of the blog")

class BlogLikeResponse(BaseModel):
    is_liked: bool
    like_count: int