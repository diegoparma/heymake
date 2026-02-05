"""
Scene Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SceneBase(BaseModel):
    """Base scene schema"""
    order: int = Field(..., ge=0)
    duration: Optional[float] = Field(None, ge=0.1, le=60)
    title: Optional[str] = Field(None, max_length=200)
    description: str = Field(..., min_length=1)
    dialogue: Optional[str] = None
    image_prompt: Optional[str] = None


class SceneCreate(SceneBase):
    """Schema para crear escena"""
    project_id: str


class SceneResponse(SceneBase):
    """Schema de respuesta de escena"""
    id: str
    project_id: str
    image_asset_id: Optional[str] = None
    video_asset_id: Optional[str] = None
    video_url: Optional[str] = None
    video_status: Optional[str] = None
    video_provider: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
