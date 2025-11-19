from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# comment creation
class CommentCreate(BaseModel):
    blog_id: str = Field(..., description="The ID of the blog being commented on")
    parent_id: Optional[str] = Field(None, description="Parent comment ID if replying to another comment; null for root comments")
    content: str = Field(..., min_length=1, max_length=300, description="Comment content")

# comment delete
class CommentDelete(BaseModel):
    comment_id: str = Field(..., description="ID of the comment to delete")

# comment response
class CommentResponse(BaseModel):
    id: str
    blog_id: str
    author_id: str
    author_username: str
    content: str
    created_at: datetime

    is_root: bool = Field(..., description="Whether this comment is a root comment")
    root_id: str = Field(..., description="ID of the root comment in this thread")
    parent_id: Optional[str] = None
    replies: Optional[List["CommentResponse"]] = None
    reply_to_comment_id: Optional[str] = Field(None,description="The comment ID this comment is replying to (can be root or non-root)",)
    reply_to_username: Optional[str] = Field(None,description="Username of the comment author being replied to",)

# root comment with paginated replies
class RootCommentResponse(CommentResponse):
    replies: List[CommentResponse] = Field(default_factory=list,description="Current page of replies under this root comment",) # 新增：该 root 下当前这一页的所有非 root 评论
    replies_page: int = Field(...,description="Current replies page number (1-based)",)  # 新增：当前 reply 页码
    replies_size: int = Field(...,description="Number of replies per page",)# 新增：reply 分页大小
    replies_total: int = Field(...,description="Total number of replies under this root comment",) # 新增：该 root 下 reply 总数
    replies_has_next: bool = Field(...,description="Whether there are more reply pages after the current one",)  # 新增：reply 是否还有下一页


# paginated root comment list for a blog
class CommentListResponse(BaseModel):
    items: List[RootCommentResponse] = Field(...,description="List of root comments for the current page",) # 新增：当前这一页的 root 评论（每个带一页 replies）
    page: int = Field(..., description="Current root comment page number (1-based)")
    size: int = Field(..., description="Number of root comments per page")
    total: int = Field(..., description="Total number of root comments for this blog")
    has_next: bool = Field(..., description="Whether there are more root comment pages")