"""
Kling Service
Servicio para animación de imágenes con Kling AI via AIMLAPI
"""
import httpx
from typing import Dict, Any, Optional
import asyncio

from app.core.config import settings


class KlingService:
    """Servicio para animación de imágenes con Kling AI via AIMLAPI"""
    
    def __init__(self):
        self.api_key = settings.KLING_API_KEY
        self.api_url = settings.KLING_API_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.model = "kling-video/v1/standard/image-to-video"
    
    async def animate_image(
        self,
        image_url: str,
        duration: int = 5,
        prompt: Optional[str] = None,
        cfg_scale: Optional[float] = None,
        negative_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Anima una imagen usando Kling AI via AIMLAPI
        
        Args:
            image_url: URL de la imagen a animar (debe ser pública)
            duration: Duración del video en segundos (5 o 10)
            prompt: Descripción del movimiento deseado
            cfg_scale: CFG scale (0-1), qué tan cercano al prompt
            negative_prompt: Elementos a evitar
        
        Returns:
            Dict con generation_id y status
        """
        
        payload = {
            "model": self.model,
            "image_url": image_url,
            "duration": duration,
        }
        
        if prompt:
            payload["prompt"] = prompt
        if cfg_scale is not None:
            payload["cfg_scale"] = cfg_scale
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/video/generations",
                headers=self.headers,
                json=payload,generation_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado de una animación en progreso
        
        Args:
            generation_id: ID de la generación retornado por animate_image
        
        Returns:
            Dict con el estado, video URL si está completo, y metadata
            Status posibles: "queued", "generating", "completed", "failed"
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/video/generations",
                headers=self.headers,
                params={"generation_id": generation_id}
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
    
    asyngeneration_id: str,
        max_wait: int = 600,
        poll_interval: int = 15
    ) -> Dict[str, Any]:
        """
        Espera a que una animación se complete
        
        Args:
            generation_id: ID de la generación
            max_wait: Tiempo máximo de espera en segundos (default 10 min)
            poll_interval: Intervalo entre consultas en segundos (default 15s)
        
        Returns:
            Dict con video URL y metadata cuando esté completo
        """
        elapsed = 0
        
        while elapsed < max_wait:
            status_data = await self.get_animation_status(generation_id)
            status = status_data.get("status")
            
            if status == "completed":
                return status_data
            elif status == "failed":
                error = status_data.get("error", {})
                raise Exception(f"Animation failed: {error.get('message', 'Unknown error')}")
            
            # Status is "queued" or "generating"elif status.get("status") == "failed":
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
