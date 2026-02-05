"""
Scenes Endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.core.database import get_turso_client
from app.schemas.scene import SceneCreate, SceneResponse

router = APIRouter()


@router.get("/project/{project_id}")
async def list_project_scenes(project_id: str):
    """Listar todas las escenas de un proyecto"""
    turso_client = get_turso_client()
    
    result = await turso_client.execute(
        """SELECT id, project_id, order_index as 'order', title, description, dialogue, 
                  image_prompt, duration, notes, status, 
                  video_url, video_status, video_provider, video_task_id,
                  created_at, updated_at 
           FROM scenes 
           WHERE project_id = ? 
           ORDER BY order_index""",
        [project_id]
    )
    
    if not result:
        return []
    
    return result


@router.get("/{scene_id}")
async def get_scene(scene_id: str):
    """Obtener una escena por ID"""
    turso_client = get_turso_client()
    
    result = await turso_client.execute(
        """SELECT id, project_id, order_index as 'order', title, description, dialogue, 
                  image_prompt, duration, notes, status, 
                  video_url, video_status, video_provider, video_task_id,
                  created_at, updated_at 
           FROM scenes 
           WHERE id = ?""",
        [scene_id]
    )
    
    if not result or len(result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    return result[0]


@router.get("/{scene_id}/assets")
async def get_scene_assets(scene_id: str):
    """Obtener los assets (imágenes, videos) de una escena"""
    turso_client = get_turso_client()
    
    result = await turso_client.execute(
        "SELECT id, scene_id, type, url, status, metadata, created_at FROM assets WHERE scene_id = ? ORDER BY created_at DESC",
        [scene_id]
    )
    
    return result if result else []


@router.get("/project/{project_id}/assets")
async def get_project_assets(project_id: str):
    """Obtener todos los assets de un proyecto"""
    turso_client = get_turso_client()
    
    # Obtener todos los scenes del proyecto primero
    scenes_result = await turso_client.execute(
        "SELECT id FROM scenes WHERE project_id = ?",
        [project_id]
    )
    
    if not scenes_result:
        return []
    
    # Obtener assets con info de la escena
    result = await turso_client.execute(
        """SELECT a.id, a.scene_id, a.type, a.url, a.status, a.metadata, a.created_at,
                  s.order_index as scene_order, s.title as scene_title
           FROM assets a
           INNER JOIN scenes s ON a.scene_id = s.id
           WHERE s.project_id = ?
           ORDER BY s.order_index, a.created_at DESC""",
        [project_id]
    )
    
    return result if result else []
