"""
Projects Endpoints
CRUD operations para proyectos
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import uuid
from datetime import datetime

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
            INSERT INTO projects (id, title, description, original_script, status, style, duration_target)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                project_id,
                project_data.title,
                project_data.description,
                project_data.original_script,
                "DRAFT",
                project_data.style,
                project_data.duration_target
            ]
        )
        
        # Obtener el proyecto creado
        result = await turso_client.execute(
            "SELECT * FROM projects WHERE id = ?",
            [project_id]
        )
        
        if not result or not result[0].get("results", {}).get("rows"):
            raise HTTPException(status_code=500, detail="Error creating project")
        
        row = result[0]["results"]["rows"][0]
        columns = result[0]["results"]["columns"]
        
        # Convertir a diccionario
        project_dict = dict(zip(columns, row))
        
        return ProjectResponse(
            id=project_dict["id"],
            title=project_dict["title"],
            description=project_dict.get("description"),
            original_script=project_dict.get("original_script"),
            status=project_dict["status"],
            style=project_dict.get("style"),
            duration_target=project_dict.get("duration_target"),
            created_at=project_dict.get("created_at"),
            updated_at=project_dict.get("updated_at")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(skip: int = 0, limit: int = 100):
    """Listar todos los proyectos"""
    try:
        result = await turso_client.execute(
            "SELECT * FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?",
            [limit, skip]
        )
        
        if not result or not result[0].get("results"):
            return []
        
        rows = result[0]["results"]["rows"]
        columns = result[0]["results"]["columns"]
        
        projects = []
        for row in rows:
            project_dict = dict(zip(columns, row))
            projects.append(ProjectResponse(
                id=project_dict["id"],
                title=project_dict["title"],
                description=project_dict.get("description"),
                original_script=project_dict.get("original_script"),
                status=project_dict["status"],
                style=project_dict.get("style"),
                duration_target=project_dict.get("duration_target"),
                created_at=project_dict.get("created_at"),
                updated_at=project_dict.get("updated_at")
            ))
        
        return projects
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
        
        if not result or not result[0].get("results", {}).get("rows"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        row = result[0]["results"]["rows"][0]
        columns = result[0]["results"]["columns"]
        project_dict = dict(zip(columns, row))
        
        return ProjectResponse(
            id=project_dict["id"],
            title=project_dict["title"],
            description=project_dict.get("description"),
            original_script=project_dict.get("original_script"),
            status=project_dict["status"],
            style=project_dict.get("style"),
            duration_target=project_dict.get("duration_target"),
            created_at=project_dict.get("created_at"),
            updated_at=project_dict.get("updated_at")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting project: {str(e)}")


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate
):
    """Actualizar un proyecto"""
    try:
        # Check if project exists
        result = await turso_client.execute(
            "SELECT id FROM projects WHERE id = ?",
            [project_id]
        )
        
        if not result or not result[0].get("results", {}).get("rows"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update fields
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar un proyecto"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    await db.delete(project)
    await db.commit()
