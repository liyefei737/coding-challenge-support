from fastapi import APIRouter

from app.api.v1.endpoints import challenges, conversations, users

api_router = APIRouter()

# Include routers for different endpoints
api_router.include_router(challenges.router, prefix="/challenges", tags=["challenges"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(users.router, prefix="/users", tags=["users"])