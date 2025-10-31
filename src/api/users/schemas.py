from pydantic import BaseModel, EmailStr, Field


# Schemas for user creation and response
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="Username between 3 and 20 characters")
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password with at least 6 characters")


# Response schema for user data
class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
