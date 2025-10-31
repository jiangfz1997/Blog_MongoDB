from fastapi import APIRouter, HTTPException, status
from src.api.users.schemas import UserCreate, UserResponse
from src.api.users.service import create_user, get_user_by_email


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user with a unique email address."
)
async def register_user(user: UserCreate):
    """
    Register a new user
    - **username**: The user's unique name.
    - **email**: The user's email address.
    - **password**: The user's plain-text password.
    - Returns: The created user object.
    """
    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    created_user = await create_user(user)
    return created_user


@router.get(
    "/email/{email}",
    summary="Get user by email",
    description="Fetch a user record by its email address.",
    response_model=UserResponse,
)
async def get_user_by_email_api(email: str):
    """
    Retrieve a user by email.

    - **email**: The email address to search for.
    - Returns: The matching user.
    """
    user = await get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user
