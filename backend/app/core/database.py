"""
Database configuration and session management
Using Turso (LibSQL) for serverless SQLite via HTTP API
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import httpx

from app.core.config import settings

# For Turso, we use httpx to interact with their HTTP API
# This is simpler than compiling libsql native bindings

class TursoClient:
    """Simple HTTP client for Turso API"""
    
    def __init__(self, url: str, auth_token: str):
        # Convert libsql:// to https://
        self.base_url = url.replace("libsql://", "https://")
        self.auth_token = auth_token
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def execute(self, sql: str, parameters: list = None):
        """Execute SQL via Turso HTTP API"""
        payload = {
            "statements": [sql] if not parameters else [{"q": sql, "params": parameters}]
        }
        response = await self.client.post("/", json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Parse Turso response format
        # Turso returns: [{"results": {"columns": [...], "rows": [[...]]}}]
        if isinstance(data, list) and len(data) > 0:
            # New format: array containing objects with "results" key
            result = data[0].get("results", {})
            if "error" in result:
                raise Exception(result["error"])
            
            columns = result.get("columns", [])
            rows = result.get("rows", [])
            
            # Convert rows to list of dicts
            return [dict(zip(columns, row)) for row in rows]
        elif "results" in data and len(data["results"]) > 0:
            # Old format: object with "results" array
            result = data["results"][0]
            if "error" in result:
                raise Exception(result["error"])
            
            columns = result.get("columns", [])
            rows = result.get("rows", [])
            
            # Convert rows to list of dicts
            return [dict(zip(columns, row)) for row in rows]
        
        return []
    
    async def close(self):
        await self.client.aclose()

# Create Turso client
turso_client = None
if settings.DATABASE_URL.startswith("libsql://"):
    turso_client = TursoClient(settings.DATABASE_URL, settings.DATABASE_AUTH_TOKEN)


def get_turso_client() -> TursoClient:
    """Get the Turso client instance"""
    if turso_client is None:
        raise RuntimeError("Turso client not initialized")
    return turso_client


# For SQLAlchemy ORM (optional - for complex queries)
# We use local SQLite for development/testing
engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    echo=settings.DATABASE_ECHO,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables
    """
    async with engine.begin() as conn:
        # Import all models here to ensure they're registered
        from app.models import project, scene, asset
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
