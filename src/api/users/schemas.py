from pydantic import BaseModel, EmailStr, Field


# Schemas for user creation and response
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$', description="Username must be 3–20 chars long and contain only letters, numbers, or underscores.")
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password with at least 6 characters")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response schema for user data
class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr

# Change password
class PasswordChange(BaseModel):
    old_password: str = Field(..., min_length=6, description="Password with at least 6 characters")
    new_password: str = Field(..., min_length=6, description="Password with at least 6 characters")

class UsernameResponse(BaseModel):
    """
    only username
    """
    username: str = Field(..., description="Username of the user")