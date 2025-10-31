# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://admin:admin123@localhost:27017/"
client = AsyncIOMotorClient(MONGO_URI)
db = client["blog_db"]
