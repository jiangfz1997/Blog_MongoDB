from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# comment creation
class CommentCreate(BaseModel):
    blog_id: str = Field(..., description="The ID of the blog being commented on")
    parent_id: Optional[str] = Field(None, description="Parent comment ID if replying to another comment")
    content: str = Field(..., min_length=1, max_length=300, description="Comment content")

# comment delete
class CommentDelete(BaseModel):
    comment_id: str = Field(..., description="ID of the comment to delete")

# comment response
class CommentResponse(BaseModel):
    id: str
    blog_id: str
    author_id: str
    parent_id: Optional[str] = None
    content: str
    replies: Optional[List["CommentResponse"]] = None
    created_at: datetime

CommentResponse.model_rebuild()