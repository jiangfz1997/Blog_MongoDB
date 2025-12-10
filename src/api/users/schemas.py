from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# Schemas for user creation and response
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$', description="Username must be 3–20 chars long and contain only letters, numbers, or underscores.")
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password with at least 6 characters")
    avatar_url: Optional[str] = Field(None, description="URL of the user's avatar image")
    bio: Optional[str] = Field(None, max_length=200, description="User bio")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response schema for user data
class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

# Change password
class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=6, description="Password with at least 6 characters")
    new_password: str = Field(..., min_length=6, description="Password with at least 6 characters")

class UserInfoResponse(BaseModel):
    username: str = Field(..., description="Username of the user")
    avatar_url: Optional[str] = Field(None, description="URL of the user's avatar image")
    bio: Optional[str] = Field(None, max_length=200, description="User bio")

class UserInfoUpdate(BaseModel):
    username: str = Field(..., description="Username of the user")
    avatar_url: Optional[str] = Field(None, description="URL of the user's avatar image")
    bio: Optional[str] = Field(None, max_length=200, description="User bio")

class UsernameCheckResult(BaseModel):
    is_available: bool = Field(..., description="Indicates if the username is available")
    message: str = Field(..., description="Additional information about the username availability")