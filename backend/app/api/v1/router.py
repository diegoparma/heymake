"""
API Router - v1
"""
from fastapi import APIRouter

from app.api.v1.endpoints import projects, scenes, assets, generation

api_router = APIRouter()


@api_router.get("/")
async def api_info():
    """API v1 information"""
    return {
        "message": "HeyMake API v1",
        "endpoints": {
            "projects": "/api/v1/projects",
            "scenes": "/api/v1/scenes",
            "assets": "/api/v1/assets",
            "generation": "/api/v1/generation",
            "docs": "/api/docs"
        }
    }


# Include all endpoint routers
api_router.include_router(
    projects.router,
    prefix="/projects",
    tags=["projects"]
)

api_router.include_router(
    scenes.router,
    prefix="/scenes",
    tags=["scenes"]
)

api_router.include_router(
    assets.router,
    prefix="/assets",
    tags=["assets"]
)

api_router.include_router(
    generation.router,
    prefix="/generation",
    tags=["generation"]
)
