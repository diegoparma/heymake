"""
Asset Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.asset import AssetType, AssetStatus


class AssetBase(BaseModel):
    """Base asset schema"""
    type: AssetType
    filename: str
    

class AssetResponse(AssetBase):
    """Schema de respuesta de asset"""
    id: str
    project_id: str
    status: AssetStatus
    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    generated_by: Optional[str] = None
    generation_prompt: Optional[str] = None
    generation_params: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
