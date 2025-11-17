# src/api/routes.py
from fastapi import APIRouter
from src.api.users.router import router as user_router
from src.api.blogs.router import router as blog_router

router = APIRouter()

router.include_router(user_router)
router.include_router(blog_router)
