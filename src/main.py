from typing import Union
from src.db.mongo import db
from src.api.routes import router as api_router
from conf.logging_config import Logger

from time import time
from fastapi import FastAPI, Request

app = FastAPI()

log = Logger('./logs/fastapi/app.log').logger
app = FastAPI()
app.include_router(api_router)


@app.middleware("http")
async def add_timing_middleware(request: Request, call_next):
    start = time()
    response = await call_next(request)
    duration = round((time() - start) * 1000, 2)
    print(f"{request.method} {request.url.path} took {duration} ms")
    response.headers["X-Process-Time-ms"] = str(duration)
    return response

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
