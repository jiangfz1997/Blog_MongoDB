# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://admin:admin123@localhost:27017/"
client = AsyncIOMotorClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,  # 发现服务器的超时（毫秒）
    connectTimeoutMS=5000,
    socketTimeoutMS=10000
)
db = client["blog_db"]

async def init_indexes():
    # blog index (author_id+created_at)
    await db.blogs.create_index(
        [("author_id", 1), ("created_at", -1)],
        name="idx_author_created"
    )

