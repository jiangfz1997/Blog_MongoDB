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
