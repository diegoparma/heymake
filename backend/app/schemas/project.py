"""
Project Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.project import ProjectStatus


class ProjectBase(BaseModel):
    """Base project schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    style: Optional[str] = None
    reference_prompt: Optional[str] = None
    duration_target: Optional[int] = Field(None, ge=1, le=600)  # 1-600 segundos


class ProjectCreate(ProjectBase):
    """Schema para crear proyecto"""
    original_script: Optional[str] = Field(None, min_length=10)


class ProjectUpdate(BaseModel):
    """Schema para actualizar proyecto"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    original_script: Optional[str] = None
    style: Optional[str] = None
    reference_prompt: Optional[str] = None
    duration_target: Optional[int] = Field(None, ge=1, le=600)
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    """Schema de respuesta del proyecto"""
    id: str
    original_script: Optional[str] = None
    status: str  # Changed from ProjectStatus enum to str for flexibility
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
