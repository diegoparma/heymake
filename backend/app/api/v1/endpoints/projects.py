"""
Projects Endpoints
CRUD operations para proyectos usando Turso HTTP API
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid

from app.core.database import turso_client
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: ProjectCreate):
    """Crear un nuevo proyecto"""
    project_id = str(uuid.uuid4())
    
    try:
        await turso_client.execute(
            """
            INSERT INTO projects (id, title, description, original_script, status, style, reference_prompt, duration_target)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                project_id,
                project_data.title,
                project_data.description,
                project_data.original_script,
                "draft",  # lowercase status
                project_data.style,
                project_data.reference_prompt,
                project_data.duration_target
            ]
        )
        
        # Obtener el proyecto creado
        result = await turso_client.execute(
            "SELECT * FROM projects WHERE id = ?",
            [project_id]
        )
        
        if not result or len(result) == 0:
            raise HTTPException(status_code=500, detail="Error creating project")
        
        return ProjectResponse(**result[0])
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error creating project: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(skip: int = 0, limit: int = 100):
    """Listar todos los proyectos"""
    try:
        result = await turso_client.execute(
            "SELECT * FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?",
            [limit, skip]
        )
        
        if not result:
            return []
        
        return [ProjectResponse(**project) for project in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing projects: {str(e)}")


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    """Obtener un proyecto por ID"""
    try:
        result = await turso_client.execute(
            "SELECT * FROM projects WHERE id = ?",
            [project_id]
        )
        
        if not result or len(result) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return ProjectResponse(**result[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting project: {str(e)}")


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, project_data: ProjectUpdate):
    """Actualizar un proyecto"""
    try:
        # Build UPDATE query dynamically
        update_data = project_data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        set_clauses = [f"{field} = ?" for field in update_data.keys()]
        values = list(update_data.values()) + [project_id]
        
        await turso_client.execute(
            f"UPDATE projects SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            values
        )
        
        # Get updated project
        result = await turso_client.execute(
            "SELECT * FROM projects WHERE id = ?",
            [project_id]
        )
        
        if not result or len(result) == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return ProjectResponse(**result[0])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str):
    """Eliminar un proyecto"""
    try:
        result = await turso_client.execute(
            "DELETE FROM projects WHERE id = ?",
            [project_id]
        )
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")
