"""
Asset Model
Representa archivos multimedia (imágenes, videos, audio)
"""
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
import uuid

from app.core.database import Base


class AssetType(str, enum.Enum):
    """Tipo de asset"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"


class AssetStatus(str, enum.Enum):
    """Estado del asset"""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Asset(Base):
    """Asset multimedia del proyecto"""
    
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Tipo y estado
    type = Column(SQLEnum(AssetType), nullable=False)
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.PENDING, nullable=False)
    
    # Información del archivo
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500))  # Path local o URL de storage
    file_size = Column(Integer)  # Tamaño en bytes
    mime_type = Column(String(100))
    
    # Dimensiones (para imágenes/videos)
    width = Column(Integer)
    height = Column(Integer)
    duration = Column(Float)  # Para videos/audio en segundos
    
    # Metadata adicional
    meta_data = Column(JSON)  # Información adicional flexible
    
    # Generación (si fue generado por IA)
    generated_by = Column(String(50))  # 'higgsfield', 'stable-diffusion', etc.
    generation_prompt = Column(Text)
    generation_params = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="assets")
    
    def __repr__(self):
        return f"<Asset {self.filename} ({self.type})>"
