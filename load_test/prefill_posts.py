"""
Prefill blogs, comments and likes

@author: Allen Pan
@date: 2025-12-02

Function：
- Use --blogs to specify the number of blogs to create
- Use --max-comments to specify the max number of comments per blog
- Read user from users_pool.json
- Produce posts_pool.json such that LIST of:
  {
    "blog_id": "692de944d2f1f59b8881fa62",
    "author_id": "692de93cd2f1f59b8881f325"
  }

Usage:
    python prefill_posts.py --blogs 20000 --max-comments 400
"""

import argparse
import json
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bson import ObjectId
from pymongo import MongoClient

# ------------------ Configuration ------------------ #

DB_NAME = "blog_db"
BLOGS_COLLECTION = "blogs"
COMMENTS_COLLECTION = "comments"

# Write batch size
BLOG_BATCH_SIZE = 500
COMMENT_BATCH_SIZE = 20

MAX_LIKES_PER_BLOG = 800


# Utilities
def load_users_pool(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"users_pool.json not found at {path}")
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        raise ValueError("users_pool.json is empty")
    for u in data:
        if "user_id" not in u:
            raise KeyError("users_pool.json record missing user_id")
    return data


def random_title():
    words = [
        "DB", "Mongo", "Shard", "Cluster", "Perf", "Test", "API", "Allen",
        "Index", "Scan", "Ops", "Bench", "Query", "Latency", "Throughput"
    ]

    # Title length no longer than 30 chars
    for _ in range(20):
        n = random.randint(2, 5)
        title = " ".join(random.choice(words) for _ in range(n))
        if len(title) < 30:
            return title

    # fall back if not generating eligible title in 20times
    return random.choice(words)


def random_paragraph(min_sentences: int = 3, max_sentences: int = 8) -> str:
    fragments = [
        "Article evident arrived express highest men did boy.",
        "Mistress sensible entirely am so.",
        "Had strictly Mrs handsome mistaken cheerful.",
        "We it so if resolution impression.",
        "By an outlived insisted procured improved am.",
        "Paid hill fine ten now love.",
        "Dispatched entreaties boisterous say why stimulated.",
        "Certain forbade picture now prevent carried she get.",
        "Cultivated who resolution connection motionless did occasional.",
        "Curiosity did its maximum dejection but uncertainty.",
    ]
    sentences = [random.choice(fragments) for _ in range(random.randint(min_sentences, max_sentences))]
    return "\n\n".join(sentences)


def random_tags():
    tag_pool = [
        "mongodb", "fastapi", "python", "performance", "testing",
        "database", "sharding", "replicaset", "index", "aggregation",
        "jwt", "locust", "benchmark", "devops", "cloud"
    ]
    n = random.randint(1, 4)
    return random.sample(tag_pool, n)


def random_past_datetime(days_back: int = 60) -> datetime:
    """generate past datetime with given number of days back"""
    now = datetime.now(timezone.utc)
    delta_days = random.randint(0, days_back)
    delta_seconds = random.randint(0, 24 * 3600)
    return now - timedelta(days=delta_days, seconds=delta_seconds)


def choose_random_users(users, k: int):
    if k <= 0:
        return []
    k = min(k, len(users))
    return random.sample(users, k)


# Logic
def prefill_posts(
        blog_count: int,
        max_comments_per_blog: int,
        mongo_uri: str,
):
    root_dir = Path(os.getcwd())
    users_pool_path = root_dir / "users_pool.json"
    users = load_users_pool(users_pool_path)

    client = MongoClient(mongo_uri)
    db = client[DB_NAME]
    blogs_col = db[BLOGS_COLLECTION]
    comments_col = db[COMMENTS_COLLECTION]

    print(f"[INFO] Connecting to MongoDB: {mongo_uri}")
    print(f"[INFO] Target collections: {DB_NAME}.{BLOGS_COLLECTION}, {DB_NAME}.{COMMENTS_COLLECTION}")
    print(f"[INFO] Users pool size: {len(users)}")
    print(f"[INFO] Will insert {blog_count} blogs, each with 0–{max_comments_per_blog} comments")

    # delect existing blogs/comments
    print("[WARN] Delete existing blogs/comments")
    blogs_col.delete_many({})
    comments_col.delete_many({})

    blogs_batch = []
    comments_batch = []
    posts_pool = []

    max_likes_per_blog = min(MAX_LIKES_PER_BLOG, len(users))

    for i in range(blog_count):
        author = random.choice(users)
        author_id_str = author["user_id"]
        author_obj_id = ObjectId(author_id_str)

        created_at = random_past_datetime(60)
        updated_at = created_at

        # create predetermine ObjectId
        blog_id = ObjectId()

        # random like
        like_num = random.randint(0, max_likes_per_blog)
        liked_users = choose_random_users(users, like_num)
        liked_by_obj_ids = [ObjectId(u["user_id"]) for u in liked_users]

        # random comment number
        comment_num = random.randint(0, max_comments_per_blog)

        # view_count = likes + comments + random int
        base_views = like_num + comment_num
        view_count = base_views + random.randint(0, 1000)

        # log payload
        blog_doc = {
            "_id": blog_id,
            "title": random_title(),
            "content": random_paragraph(),
            "author_id": author_id_str, \
            "created_at": created_at,
            "updated_at": updated_at,
            "tags": random_tags(),
            "view_count": int(view_count),
            "like_count": int(like_num),
            "liked_by": liked_by_obj_ids,  # ObjectId array
            "comment_count": int(comment_num),
        }
        blogs_batch.append(blog_doc)

        # write to posts_pool
        posts_pool.append(
            {
                "blog_id": str(blog_id),
                "author_id": author_id_str,
            }
        )

        # generate commnets
        comments_for_this_blog = []

        if comment_num > 0:
            max_root_per_blog = min(20, comment_num)
            root_count = random.randint(1, max_root_per_blog)

            root_comments_meta = []

            # generate root comments
            for _ in range(root_count):
                commenter = random.choice(users)
                commenter_id_str = commenter["user_id"]
                commenter_username = commenter["username"]

                c_id = ObjectId()
                c_created = random_past_datetime(60)

                # comment payload
                root_doc = {
                    "_id": c_id,
                    "content": random_paragraph(1, 2),
                    "blog_id": str(blog_id),
                    "author_id": commenter_id_str,
                    "created_at": c_created,
                    "is_root": True,
                    "root_id": str(c_id),
                    "parent_id": None,
                    "reply_to_comment_id": None,
                    "reply_to_username": None,
                }
                comments_for_this_blog.append(root_doc)

                root_comments_meta.append(
                    {
                        "root_id": str(c_id),
                        "last_comment_id": str(c_id),
                        "last_author_username": commenter_username,
                    }
                )

            # generate reply comments
            remaining_replies = comment_num - root_count

            for _ in range(remaining_replies):
                meta = random.choice(root_comments_meta)

                target_comment_id = meta["last_comment_id"]
                target_username = meta["last_author_username"]

                replier = random.choice(users)
                replier_id_str = replier["user_id"]
                replier_username = replier["username"]

                c_id = ObjectId()
                c_created = random_past_datetime(60)

                # comment payload
                reply_doc = {
                    "_id": c_id,
                    "content": random_paragraph(1, 2),
                    "blog_id": str(blog_id),
                    "author_id": replier_id_str,
                    "created_at": c_created,
                    "is_root": False,
                    "root_id": meta["root_id"],
                    "parent_id": target_comment_id,
                    "reply_to_comment_id": target_comment_id,
                    "reply_to_username": target_username,
                }
                comments_for_this_blog.append(reply_doc)

                # update thread
                meta["last_comment_id"] = str(c_id)
                meta["last_author_username"] = replier_username

        comments_batch.extend(comments_for_this_blog)

        # write rate control
        if len(blogs_batch) >= BLOG_BATCH_SIZE:
            blogs_col.insert_many(blogs_batch)
            blogs_batch.clear()

        if len(comments_batch) >= COMMENT_BATCH_SIZE:
            comments_col.insert_many(comments_batch)
            comments_batch.clear()

        if (i + 1) % 1000 == 0 or (i + 1) == blog_count:
            print(f"[INFO] Prepared {i + 1}/{blog_count} blogs")

    # inset remaining
    if blogs_batch:
        blogs_col.insert_many(blogs_batch)
    if comments_batch:
        comments_col.insert_many(comments_batch)

    print("[INFO] Finished inserting blogs and comments")

    # save to posts_pool.json
    posts_pool_path = root_dir / "posts_pool.json"
    with posts_pool_path.open("w", encoding="utf-8") as f:
        json.dump(posts_pool, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Saved posts pool to {posts_pool_path}")
    print(f"[DONE] Prefill completed")


def main():
    parser = argparse.ArgumentParser(
        description="Prefill MongoDB with blogs, comments and likes for performance testing"
    )
    parser.add_argument(
        "--blogs",
        type=int,
        default=3000,
        help=f"Number of blogs to insert (default: 3000)",
    )
    parser.add_argument(
        "--max-comments",
        type=int,
        default=40,
        help=f"Maximum number of comments per blog (default: 40)",
    )
    parser.add_argument(
        "--mongo-uri",
        type=str,
        default="mongodb://localhost:27017",
        help=f"MongoDB connection URI (default: mongodb://localhost:27017)",
    )
    args = parser.parse_args()

    prefill_posts(
        blog_count=args.blogs,
        max_comments_per_blog=args.max_comments,
        mongo_uri=args.mongo_uri,
    )


if __name__ == "__main__":
    main()
