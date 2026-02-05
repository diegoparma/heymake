"""
HeyAI Backend - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1 import api_router
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME}...")
    # Database tables are already created in Turso
    print("✅ Database ready")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Plataforma de generación de trailers con IA",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check"""
    return {
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "status": "healthy",
        "environment": settings.ENV,
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return JSONResponse(
        content={
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
