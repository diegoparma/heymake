"""
Application Configuration
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "HeyAI"
    ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Database - Turso
    DATABASE_URL: str
    DATABASE_AUTH_TOKEN: str = ""
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str
    
    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # LLM APIs
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_AI_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4-turbo-preview"
    
    # Higgsfield AI
    HIGGSFIELD_API_KEY_ID: str = ""
    HIGGSFIELD_API_KEY_SECRET: str = ""
    HIGGSFIELD_API_URL: str = "https://api.higgsfield.ai/v1"
    
    # Kling AI
    KLING_API_KEY: str
    KLING_API_URL: str = "https://api.klingai.com/v1"
    
    # Storage - Google Drive
    STORAGE_PROVIDER: str = "local"
    GOOGLE_DRIVE_CREDENTIALS_FILE: str = "credentials.json"
    GOOGLE_DRIVE_FOLDER_ID: str = ""
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 50  # MB
    ALLOWED_VIDEO_FORMATS: str = "mp4,mov,avi,mkv"
    ALLOWED_IMAGE_FORMATS: str = "jpg,jpeg,png,webp"
    
    # Processing
    MAX_CONCURRENT_TASKS: int = 3
    VIDEO_OUTPUT_FORMAT: str = "mp4"
    VIDEO_QUALITY: str = "high"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_video_formats_list(self) -> List[str]:
        """Parse allowed video formats into a list"""
        return [fmt.strip() for fmt in self.ALLOWED_VIDEO_FORMATS.split(",")]
    
    @property
    def allowed_image_formats_list(self) -> List[str]:
        """Parse allowed image formats into a list"""
        return [fmt.strip() for fmt in self.ALLOWED_IMAGE_FORMATS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
