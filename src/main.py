from typing import Union

from fastapi import FastAPI
from src.db.mongo import db
from src.api.routes import router as api_router

app = FastAPI()
app.include_router(api_router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/fetch")
async def fetch():
    count = await db.posts.count_documents({})
    return {"message": f"Connected to MongoDB! Posts in DB: {count}"}
