from typing import Union
from src.db.mongo import db, init_indexes
from src.api.routes import router as api_router
from src.logger import logger,setup_logging
from fastapi.middleware.cors import CORSMiddleware
from time import time
from fastapi import FastAPI, Request
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager
from src.api.blogs.service import get_hottest_tags
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        get_hottest_tags,
        'interval',
        minutes=10,
        id='calc_hot_tags',
        replace_existing=True,
        misfire_grace_time=60
    )

    from datetime import datetime, timedelta
    scheduler.add_job(
        get_hottest_tags,
        'date',
        run_date=datetime.now() + timedelta(seconds=1),
        id='calc_hot_tags_immediate'
    )

    scheduler.start()
    try:
        await get_hottest_tags()
        print("Initial data loaded to Redis")
    except Exception as e:
        print(f"Failed to load initial data: {e}")

    yield
    scheduler.shutdown()
app = FastAPI(lifespan=lifespan)
scheduler = AsyncIOScheduler()
setup_logging()
logger.info("Starting app")
app.include_router(api_router)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    f"http://10.0.0.23:5173",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    # allow_origin_regex=r"^https?://.*:5173$",
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
allow_origins = [],

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
    logger.debug(f"{request.method} {request.url.path} took {duration} ms")
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


