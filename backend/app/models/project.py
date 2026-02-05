"""
Project Model
Representa un proyecto de trailer/publicidad
"""
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    """Estado del proyecto"""
    DRAFT = "draft"
    PROCESSING_SCRIPT = "processing_script"
    GENERATING_IMAGES = "generating_images"
    ANIMATING_SCENES = "animating_scenes"
    READY_FOR_EDIT = "ready_for_edit"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base):
    """Proyecto de trailer/publicidad"""
    
    __tablename__ = "projects"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Script/Guión original
    original_script = Column(Text, nullable=False)
    
    # Estado del proyecto
    status = Column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.DRAFT,
        nullable=False
    )
    
    # Configuración
    style = Column(String(100))  # cinematográfico, publicitario, etc.
    duration_target = Column(Integer)  # duración objetivo en segundos
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.title} ({self.status})>"
