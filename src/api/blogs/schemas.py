from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# blog creation
class BlogCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=30, description="Blog title between 3 and 30 characters")
    content: str = Field(..., min_length=10, description="Blog content, at least 10 characters")


# blog update
class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=30)
    content: Optional[str] = Field(None, min_length=10)


# blog delete
class BlogDelete(BaseModel):
    blog_id: str = Field(..., description="ID of the blog to delete")


# blog response
class BlogResponse(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None