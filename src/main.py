from typing import Union
from src.db.mongo import db, init_indexes
from src.api.routes import router as api_router
from src.logger import logger,setup_logging
from fastapi.middleware.cors import CORSMiddleware
from time import time
from fastapi import FastAPI, Request

app = FastAPI()

setup_logging()
logger.info("Starting app")
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"   # <- Vite dev server 的 origin，生产环境改成真实域名
    ],
    allow_credentials=True,      # <- 允许 cookie / Authorization header 等被发送
    allow_methods=["*"],         # <- 允许的 HTTP 方法，'*' 表示所有
    allow_headers=["*"],         # <- 允许的请求头
)

@app.on_event("startup")
async def on_startup():
    logger.info("Initializing MongoDB indexes...")
    await init_indexes()
    logger.info("MongoDB indexes initialized")

@app.middleware("http")
async def add_timing_middleware(request: Request, call_next):
    start = time()
    response = await call_next(request)
    duration = round((time() - start) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} took {duration} ms")
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
