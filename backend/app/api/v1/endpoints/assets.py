"""
Assets Endpoints
Endpoints para gestionar y servir archivos estáticos
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pathlib import Path

from app.core.database import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetResponse

router = APIRouter()

# Directorios de almacenamiento
UPLOADS_DIR = Path("uploads")
IMAGES_DIR = UPLOADS_DIR / "images"
VIDEOS_DIR = UPLOADS_DIR / "videos"

# Asegurar que existan los directorios
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/project/{project_id}", response_model=List[AssetResponse])
async def list_project_assets(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Listar todos los assets de un proyecto"""
    result = await db.execute(
        select(Asset)
        .where(Asset.project_id == project_id)
        .order_by(Asset.created_at.desc())
    )
    assets = result.scalars().all()
    return assets


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener un asset por ID"""
    result = await db.execute(
        select(Asset).where(Asset.id == asset_id)
    )
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found"
        )
    
    return asset


@router.post("/upload/{project_id}", response_model=AssetResponse)
async def upload_asset(
    project_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Subir un asset al proyecto"""
    # TODO: Implementar lógica de guardado de archivo
    # Por ahora retornamos un placeholder
    
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Upload functionality coming soon"
    )


@router.get("/image/{filename}")
async def get_image(filename: str):
    """
    Sirve una imagen desde el almacenamiento local
    """
    file_path = IMAGES_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Verificar que el archivo esté dentro del directorio permitido (seguridad)
    try:
        file_path.resolve().relative_to(IMAGES_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        file_path,
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=31536000"}
    )


@router.get("/video/{filename}")
async def get_video(filename: str):
    """
    Sirve un video desde el almacenamiento local
    """
    file_path = VIDEOS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Verificar que el archivo esté dentro del directorio permitido
    try:
        file_path.resolve().relative_to(VIDEOS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return FileResponse(
        file_path,
        media_type="video/mp4",
        headers={"Cache-Control": "public, max-age=31536000"}
    )
