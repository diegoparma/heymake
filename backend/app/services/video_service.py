"""
Kling Service
Servicio para animación de imágenes con Kling AI
"""
import httpx
from typing import Dict, Any, Optional
import asyncio

from app.core.config import settings


class KlingService:
    """Servicio para animación de imágenes con Kling AI"""
    
    def __init__(self):
        self.api_key = settings.KLING_API_KEY
        self.api_url = settings.KLING_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def animate_image(
        self,
        image_url: str,
        duration: float = 5.0,
        motion_type: str = "auto",
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Anima una imagen usando Kling AI
        
        Args:
            image_url: URL de la imagen a animar
            duration: Duración del video en segundos (típicamente 5-10s)
            motion_type: Tipo de movimiento ('auto', 'zoom_in', 'zoom_out', 'pan_left', 'pan_right')
            additional_params: Parámetros adicionales de Kling
        
        Returns:
            Dict con información del video generado
        """
        
        payload = {
            "image_url": image_url,
            "duration": duration,
            "motion_type": motion_type,
        }
        
        if additional_params:
            payload.update(additional_params)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/animate",
                headers=self.headers,
                json=payload,
                timeout=180.0  # 3 minutos de timeout
            )
            
            response.raise_for_status()
            return response.json()
    
    async def get_animation_status(self, task_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado de una animación en progreso
        
        Args:
            task_id: ID de la tarea de animación
        
        Returns:
            Dict con el estado y URL del video si está completo
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/tasks/{task_id}",
                headers=self.headers
            )
            
            response.raise_for_status()
            return response.json()
    
    async def wait_for_animation(
        self,
        task_id: str,
        max_wait: int = 300,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Espera a que una animación se complete
        
        Args:
            task_id: ID de la tarea
            max_wait: Tiempo máximo de espera en segundos
            poll_interval: Intervalo entre consultas en segundos
        
        Returns:
            Dict con información del video completado
        """
        elapsed = 0
        
        while elapsed < max_wait:
            status = await self.get_animation_status(task_id)
            
            if status.get("status") == "completed":
                return status
            elif status.get("status") == "failed":
                raise Exception(f"Animation failed: {status.get('error')}")
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Animation did not complete within {max_wait} seconds")
    
    async def download_video(self, video_url: str) -> bytes:
        """
        Descarga un video generado
        
        Args:
            video_url: URL del video a descargar
        
        Returns:
            Contenido del video en bytes
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url)
            response.raise_for_status()
            return response.content


# Singleton instance
kling_service = KlingService()
