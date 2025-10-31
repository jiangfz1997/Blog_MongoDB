# app/api/users/service.py
from src.db.mongo import db
from src.api.users.schemas import UserCreate
from src.api.users.utils import hash_password
from bson import ObjectId


# User creation service
async def create_user(user_data: UserCreate):
    # password encryption
    print("user_data.password:", user_data.password)
    hashed_pw = hash_password(user_data.password)

    user = {
        "username": user_data.username,
        "email": user_data.email,
        "password": hashed_pw,
    }
    result = await db.users.insert_one(user)

    created_user = await db.users.find_one({"_id": result.inserted_id})
    created_user["id"] = str(created_user["_id"])
    del created_user["password"]

    return created_user


# Fetch user by email
async def get_user_by_email(email: str):
    user = await db.users.find_one({"email": email})
    if user:
        user["id"] = str(user["_id"])
        del user["password"]
    return user
