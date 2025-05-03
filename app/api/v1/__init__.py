"""API v1 package."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, diaries

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(diaries.router, prefix="/diaries", tags=["diaries"]) 