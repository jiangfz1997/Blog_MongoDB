"""
Create test users

@author: Allen Pan
@date: 2025-12-02

Function:
- Use --count to specify the number of users to create
- Insert into blog_db.users, and hashing password are the same for all users
- Produce "users_pool.json" such that LIST of:
  {
    "user_id": "692de93cd2f1f59b8881f288",
    "username": "MTS1aJ",
    "email": "mts1aj@example.com",
    "password": "panyilun@Test#123!"
  }

Usage:
    python create_test_users.py --count 999
"""

import argparse
import json
import os
import random
import string

from pymongo import MongoClient

# utils.py
from src.api.users.utils import hash_password


# Configuration
DB_NAME = "blog_db"
USERS_COLLECTION = "users"

AVATAR_OPTIONS = [
    "https://api.dicebear.com/9.x/adventurer/svg?seed=Felix",
    "https://api.dicebear.com/9.x/adventurer/svg?seed=Aneka",
    "https://api.dicebear.com/9.x/adventurer/svg?seed=Milo",
    "https://api.dicebear.com/9.x/adventurer/svg?seed=Lia",
    "https://api.dicebear.com/9.x/adventurer/svg?seed=Christopher",
]

DEFAULT_PLAIN_PASSWORD = "panyilun@Test#123!"


# Utilities
def random_id(min_len: int = 6, max_len: int = 12) -> str:
    """6 - 12 digits random id"""
    length = random.randint(min_len, max_len)
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def random_email(user_id: str, domain: str = "uwo.ca") -> str:
    """generate email"""
    return f"{user_id.lower()}@{domain}"


def random_avatar_url() -> str:
    """Random avatar picker"""
    return random.choice(AVATAR_OPTIONS)


def random_bio(min_words: int = 3, max_words: int = 10) -> str:
    """40 -50 words random bio"""
    word_pool = [
        "curious", "developer", "exploring", "modern", "web", "technology",
        "learning", "database", "design", "and", "distributed", "systems",
        "enjoys", "reading", "about", "performance", "tuning", "and",
        "experimenting", "with", "new", "frameworks", "loves", "teaching",
        "sharing", "ideas", "with", "friends", "and", "building", "side",
        "projects", "in", "free", "time", "interested", "in", "cloud",
        "computing", "networking", "and", "open", "source", "software",
        "always", "trying", "to", "improve", "skills", "and", "learn",
        "something", "new", "every", "day"
    ]
    n = random.randint(min_words, max_words)
    words = [random.choice(word_pool) for _ in range(n)]
    # Capital char for first word and ends in period
    sentence = " ".join(words)
    return sentence[0].upper() + sentence[1:] + "."


# Logics
def create_test_users(count: int, mongo_uri: str):
    client = MongoClient(mongo_uri)
    db = client[DB_NAME]
    users_col = db[USERS_COLLECTION]

    print(f"[INFO] Connecting to MongoDB: {mongo_uri}")
    print(f"[INFO] Target collection: {DB_NAME}.{USERS_COLLECTION}")
    print(f"[INFO] Will create {count} users")

    print("[WARN] Delete existing users")
    users_col.delete_many({})

    docs = []
    # user infor withOUT ObjectId
    credentials = []

    # all test account use one hashed password
    password_hash = hash_password(DEFAULT_PLAIN_PASSWORD)

    remaining = count
    while remaining > 0:
        user_id = random_id()
        email = random_email(user_id)
        avatar_url = random_avatar_url()
        bio = random_bio()
        if len(bio) >= 200:
            continue

        doc = {
            "username": user_id,
            "email": email,
            "password": password_hash,
            "avatar_url": avatar_url,
            "bio": bio,
        }
        docs.append(doc)

        # user info need to be saved
        credentials.append(
            {
                "username": user_id,
                "email": email,
                "password": DEFAULT_PLAIN_PASSWORD,
            }
        )

        remaining -= 1

    if not docs:
        print("[WARN] No users to insert")
        return

    # Insert into database
    result = users_col.insert_many(docs)
    inserted_ids = result.inserted_ids
    print(f"[INFO] Inserted {len(inserted_ids)} users into {DB_NAME}.{USERS_COLLECTION}")

    # Get ObjectId and create users_pool.json
    pool_for_locust = []
    for obj_id, cred in zip(inserted_ids, credentials):
        pool_for_locust.append(
            {
                "user_id": str(obj_id),
                "username": cred["username"],
                "email": cred["email"],
                "password": cred["password"],
            }
        )

    # Save created account info to json
    pool_path = os.path.join(os.getcwd(), "users_pool.json")
    with open(pool_path, "w", encoding="utf-8") as f:
        json.dump(pool_for_locust, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Saved user pool to {pool_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Create test users in MongoDB for performance testing"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=2000,
        help="Number of test users to create (default: 2000)",
    )
    parser.add_argument(
        "--mongo-uri",
        type=str,
        default="mongodb://localhost:27017",
        help=f"MongoDB connection URI (default: mongodb://localhost:27017)",
    )
    args = parser.parse_args()

    create_test_users(count=args.count, mongo_uri=args.mongo_uri)
