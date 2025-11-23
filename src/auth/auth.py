# auth.py
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Request, status
from jose import jwt, JWTError
from bson import ObjectId
from src.db.mongo import db

import os

SECRET_KEY = os.environ.get("SECRET_KEY", "DEFAULTSECRETKEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set")
ALGORITHM = "HS256"



def create_access_token(data: dict, expires_minutes: int = 15):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_days: int = 7):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=expires_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(request: Request):

    token = request.cookies.get("access_token")

    if not token:
        authz = request.headers.get("Authorization", "")
        if authz.startswith("Bearer "):
            token = authz.split(" ", 1)[1]

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    if "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    return payload


def get_token_from_request(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    if not token:
        authz = request.headers.get("Authorization", "")
        if authz.startswith("Bearer "):
            token = authz.split(" ", 1)[1]
    return token


async def get_current_user(
        payload: dict = Depends(verify_access_token)  # 先拿到 payload
):

    user_id = payload.get("sub")

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID format")


    user = await db.users.find_one({"_id": ObjectId(user_id)})

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user["id"] = str(user["_id"])
    return user


async def try_get_current_user(request: Request) -> dict | None:

    token = get_token_from_request(request)
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id or not ObjectId.is_valid(user_id):
            return None

        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        user["id"] = str(user["_id"])
        return user

    except JWTError:
        return None
    except Exception:
        return None

