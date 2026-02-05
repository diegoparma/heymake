"""
Generation Schemas
Schemas para los endpoints de generación de contenido
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ScriptAnalysisRequest(BaseModel):
    """Request para analizar guión"""
    project_id: str
    script: str = Field(..., min_length=10)
    style: Optional[str] = "cinematic"
    num_scenes: Optional[int] = Field(None, ge=1, le=50)
    duration_target: Optional[int] = Field(None, ge=1, le=600)


class SceneBreakdown(BaseModel):
    """Escena generada por el LLM"""
    order: int
    title: str
    description: str
    dialogue: Optional[str] = None
    image_prompt: str
    duration: Optional[float] = None
    notes: Optional[str] = None


class ScriptAnalysisResponse(BaseModel):
    """Response del análisis de guión"""
    project_id: str
    scenes: List[SceneBreakdown]
    total_scenes: int
    estimated_duration: float
    style: Optional[str] = "cinematic"
    summary: Optional[str] = None


class ImageGenerationRequest(BaseModel):
    """Request para generar imagen"""
    prompt: str
    style: Optional[str] = None
    width: Optional[int] = 1024
    height: Optional[int] = 768
    additional_params: Optional[Dict[str, Any]] = None


class ImageGenerationResponse(BaseModel):
    """Response de generación de imagen"""
    asset_id: str
    image_url: str
    status: str
    generation_time: float


class VideoGenerationRequest(BaseModel):
    """Request para generar video desde imagen"""
    scene_id: str
    image_url: str
    duration: Optional[float] = Field(default=5.0, ge=1.0, le=10.0)
    motion_type: Optional[str] = Field(default="auto", description="auto, zoom_in, zoom_out, pan_left, pan_right")
    additional_params: Optional[Dict[str, Any]] = None


class VideoGenerationResponse(BaseModel):
    """Response de generación de video"""
    scene_id: str
    task_id: str
    status: str
    message: str


class VideoStatusResponse(BaseModel):
    """Response del estado de generación de video"""
    task_id: str
    status: str
    video_url: Optional[str] = None
    progress: Optional[int] = None
    error: Optional[str] = None


class ProjectVideosRequest(BaseModel):
    """Request para generar videos de todo el proyecto"""
    project_id: str
    duration: Optional[float] = Field(default=5.0, ge=1.0, le=10.0)
    motion_type: Optional[str] = "auto"
