# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from src.utils.monitor import MongoQueryMonitor

monitor = MongoQueryMonitor()
mongo_url = os.getenv("MONGODB_URL", "mongodb://admin:admin123@localhost:27017/")
client = AsyncIOMotorClient(
    mongo_url,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
    socketTimeoutMS=10000,
    event_listeners=[monitor]
)
db = client["blog_db"]

async def init_indexes():
    # blog index (author_id+created_at)
    await db.blogs.create_index(
        [("author_id", 1), ("created_at", -1)],
        name="idx_author_created"
    )

