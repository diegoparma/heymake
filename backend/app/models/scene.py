"""
Scene Model
Representa una escena individual del trailer
"""
from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Scene(Base):
    """Escena individual del proyecto"""
    
    __tablename__ = "scenes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    
    # Orden y timing
    order = Column(Integer, nullable=False)
    duration = Column(Float)  # duración en segundos
    
    # Contenido
    title = Column(String(200))
    description = Column(Text, nullable=False)  # Descripción visual de la escena
    dialogue = Column(Text)  # Diálogo o texto si hay
    
    # Prompt para generación de imagen
    image_prompt = Column(Text)  # Prompt optimizado para Higgsfield
    
    # Referencias a assets generados
    image_asset_id = Column(String, ForeignKey("assets.id"))
    video_asset_id = Column(String, ForeignKey("assets.id"))
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="scenes")
    image_asset = relationship("Asset", foreign_keys=[image_asset_id])
    video_asset = relationship("Asset", foreign_keys=[video_asset_id])
    
    def __repr__(self):
        return f"<Scene {self.order}: {self.title}>"
