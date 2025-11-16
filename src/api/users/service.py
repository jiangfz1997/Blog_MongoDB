# app/api/users/service.py
import asyncio
from src.db.mongo import db
from . import repository
from src.api.users.schemas import UserCreate
from src.api.users.utils import hash_password, verify_password
from src.logger import get_logger
from src.auth import auth
from typing import Tuple
from bson import ObjectId
from fastapi import HTTPException, status
from src.db.mongo import db
logger = get_logger(__name__)

async def create_user(user_in: UserCreate) -> Tuple[dict, str, str]:

    existing = await asyncio.wait_for(repository.find_by_email(db, user_in.email), timeout=5)
    if existing:
        raise ValueError("Email already registered")

    hashed = hash_password(user_in.password)
    user_doc = {"username": user_in.username, "email": user_in.email, "password": hashed}
    created = await asyncio.wait_for(repository.insert_user(db, user_doc), timeout=5)

    payload = {"sub": created["id"], "email": created["email"]}
    access = auth.create_access_token(payload)
    refresh = auth.create_refresh_token(payload)
    return created, access, refresh

# Fetch user by email
async def get_user_by_email(email: str):
    user = await db.users.find_one({"email": email})
    if user:
        user["id"] = str(user["_id"])
        del user["password"]
    return user

# check password
async def authenticate_user(email: str, password: str):
    user_doc = await repository.find_by_email(db, email)
    if not user_doc:
        return None
    if not verify_password(password, user_doc["password"]):
        return None
    # sanitize
    user = {
        "id": str(user_doc["_id"]),
        "username": user_doc["username"],
        "email": user_doc["email"],
        "avatarUrl": user_doc.get("avatarUrl", "")
    }
    return user

# change password
async def change_password(user_id: str, old_password: str, new_password: str) -> None:
    user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # check old pw
    if not verify_password(old_password, user_doc["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Old password is incorrect")

    new_hash = hash_password(new_password)

    ok = await repository.update_password_hash(db, ObjectId(user_id), new_hash)
    if not ok:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update password")