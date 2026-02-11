"""
Unified Video Service
Servicio unificado para generación de videos con múltiples proveedores
"""
from typing import Dict, Any, Optional, Literal
from app.services.video_service import kling_service
from app.services.sora_service import sora_service

# Import lazy for optional providers to avoid hard failures when deps no están
try:
    from app.services.veo_service import veo_service  # type: ignore
    _veo_available = True
except Exception as exc:
    veo_service = None  # type: ignore
    _veo_available = False
    print(f"⚠️ Veo service no disponible: {exc}")
from app.core.config import settings


VideoProvider = Literal["kling", "veo", "sora", "runway", "pika"]


class UnifiedVideoService:
    """Servicio unificado que maneja múltiples proveedores de video"""
    
    def __init__(self):
        self.providers = {
            "kling": kling_service,
            "sora": sora_service,
        }
        if _veo_available:
            self.providers["veo"] = veo_service  # type: ignore
        # Preparado para futuros proveedores:
        # "runway": runway_service,
        # "pika": pika_service,
        
        self.default_provider = "veo" if _veo_available else "sora"
    
    def get_provider(self, provider: Optional[str] = None):
        """Obtiene el servicio del proveedor especificado"""
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Unknown video provider: {provider_name}. Available: {list(self.providers.keys())}")
        
        return self.providers[provider_name]
    
    async def animate_image(
        self,
        image_url: str,
        duration: float = 5.0,
        motion_type: str = "auto",
        provider: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Anima una imagen usando el proveedor especificado
        
        Args:
            image_url: URL de la imagen a animar
            duration: Duración del video en segundos
            motion_type: Tipo de movimiento
            provider: Proveedor a usar (kling, veo, etc.)
            additional_params: Parámetros adicionales
        
        Returns:
            Dict con información del video y el proveedor usado
        """
        service = self.get_provider(provider)
        result = await service.animate_image(
            image_url=image_url,
            duration=duration,
            motion_type=motion_type,
            additional_params=additional_params
        )
        
        # Agregar información del proveedor
        result["provider"] = provider or self.default_provider
        return result
    
    async def generate_from_text(
        self,
        prompt: str,
        duration: float = 5.0,
        aspect_ratio: str = "16:9",
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Genera un video desde texto
        
        Args:
            prompt: Descripción del video
            duration: Duración en segundos
            aspect_ratio: Relación de aspecto
            provider: Proveedor a usar
        
        Returns:
            Dict con información del video generado
        """
        service = self.get_provider(provider)
        
        # Solo algunos proveedores soportan text-to-video
        if hasattr(service, 'generate_from_text'):
            result = await service.generate_from_text(
                prompt=prompt,
                duration=duration,
                aspect_ratio=aspect_ratio
            )
            result["provider"] = provider or self.default_provider
            return result
        else:
            return {
                "success": False,
                "error": f"Provider {provider or self.default_provider} does not support text-to-video generation"
            }
    
    async def get_animation_status(
        self,
        task_id: str,
        provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtiene el estado de una animación
        
        Args:
            task_id: ID de la tarea
            provider: Proveedor usado (se puede inferir del task_id)
        
        Returns:
            Dict con el estado del video
        """
        service = self.get_provider(provider)
        return await service.get_animation_status(task_id)
    
    async def wait_for_animation(
        self,
        task_id: str,
        provider: Optional[str] = None,
        max_wait: int = 300,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Espera a que una animación se complete
        
        Args:
            task_id: ID de la tarea
            provider: Proveedor usado
            max_wait: Tiempo máximo de espera en segundos
            poll_interval: Intervalo entre consultas en segundos
        
        Returns:
            Dict con información del video completado
        """
        service = self.get_provider(provider)
        return await service.wait_for_animation(
            task_id=task_id,
            max_wait=max_wait,
            poll_interval=poll_interval
        )
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        Lista todos los proveedores disponibles y sus capacidades
        
        Returns:
            Dict con información de cada proveedor
        """
        providers_info = {
            "kling": {
                "name": "Kling AI",
                "available": True,
                "features": ["image-to-video"],
                "max_duration": 10,
                "resolutions": ["720p", "1080p"],
                "motion_types": ["auto", "zoom_in", "zoom_out", "pan_left", "pan_right"]
            },
            "sora": {
                "name": "OpenAI Sora",
                "available": True,
                "features": ["text-to-video", "image-to-video"],
                "max_duration": None,
                "resolutions": ["auto"],
                "aspect_ratios": ["16:9", "9:16"],
                "note": "Usa OPENAI_API_KEY; endpoints pueden variar según acceso"
            }
        }
        if _veo_available:
            providers_info["veo"] = {
                "name": "Google Veo 3.1",
                "available": True,
                "features": ["image-to-video", "text-to-video"],
                "max_duration": 8,
                "resolutions": ["720p", "1080p", "4k"],
                "aspect_ratios": ["16:9", "9:16"],
                "note": "Uses same GOOGLE_AI_API_KEY as Gemini"
            }
        else:
            providers_info["veo"] = {
                "name": "Google Veo 3.1",
                "available": False,
                "features": ["image-to-video", "text-to-video"],
                "max_duration": 8,
                "resolutions": ["720p", "1080p", "4k"],
                "aspect_ratios": ["16:9", "9:16"],
                "note": "Dependencia google-genai no instalada"
            }
        return providers_info


# Singleton instance
unified_video_service = UnifiedVideoService()
