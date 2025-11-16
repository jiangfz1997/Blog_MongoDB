from fastapi import APIRouter, HTTPException, status, Depends
from src.api.users.schemas import *
from src.api.users.service import *
from src.logger import get_logger
from fastapi.encoders import jsonable_encoder
from src.api.users.schemas import PasswordChange

logger = get_logger(__name__)
router = APIRouter(
    prefix="/users",
    tags=["users"],
)
from bson import ObjectId
from src.auth.auth import create_access_token, create_refresh_token
from fastapi import APIRouter, Response, status
from fastapi.responses import JSONResponse
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user with a unique email address."
)
async def register_user(user: UserCreate):
    """
    Register a new user and set JWT tokens in cookies.
    - **user**: UserCreate object containing username, email, and password.
    - Returns: UserResponse object of the created user.
    """
    try:
        created, access_token, refresh_token = await create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    resp_body = {"user": created}
    response = JSONResponse(status_code=status.HTTP_201_CREATED, content=jsonable_encoder(resp_body))
    response.set_cookie("access_token", access_token, httponly=True, secure=False, samesite="lax")
    response.set_cookie("refresh_token", refresh_token, httponly=True, secure=False, samesite="lax")
    return response

@router.post(
    "/login",
    response_model=UserResponse,
    summary="User login",
    description="Authenticate user and return JWT tokens in cookies."
)
async def login_user(credentials: UserLogin):
    """
    Authenticate user and set JWT tokens in cookies.
    - **credentials**: UserLogin object containing email and password.
    - Returns: UserResponse object of the authenticated user.
    """
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # generate tokens
    payload = {"sub": user["id"], "email": user["email"]}
    access = create_access_token(payload)
    refresh = create_refresh_token(payload)
    resp = JSONResponse(content=jsonable_encoder({"user": user}))
    resp.set_cookie("access_token", access, httponly=True, secure=False, samesite="lax")
    resp.set_cookie("refresh_token", refresh, httponly=True, secure=False, samesite="lax")
    return resp

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

#change password
@router.post(
    "/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password",
    description="Change password after login",
)
async def change_password_endpoint(data: PasswordChange, claims: dict = Depends(auth.verify_access_token)):
    user_id = claims["sub"]
    await change_password(user_id, data.old_password, data.new_password)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

#log out
@router.post(
    "/logout",
    summary="Logout user",
    description="Clear JWT tokens from cookies to logout."
)
async def logout_user():
    """
    Remove access and refresh tokens from cookies.
    """
    response = JSONResponse(
        content={"message": "Successfully logged out"},
        status_code=200
    )
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response