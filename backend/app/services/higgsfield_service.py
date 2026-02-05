"""
Higgsfield Service
Servicio para interactuar con la API de Higgsfield
"""
import httpx
from typing import Dict, Any, Optional

from app.core.config import settings


class HiggsfieldService:
    """Servicio para generación de imágenes con Higgsfield"""
    
    def __init__(self):
        self.api_key_id = settings.HIGGSFIELD_API_KEY_ID
        self.api_key_secret = settings.HIGGSFIELD_API_KEY_SECRET
        self.api_url = settings.HIGGSFIELD_API_URL
        self.headers = {
            "X-API-Key-ID": self.api_key_id,
            "X-API-Key-Secret": self.api_key_secret,
            "Content-Type": "application/json"
        }
    
    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 768,
        style: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera una imagen usando Higgsfield
        
        Args:
            prompt: Descripción de la imagen a generar
            width: Ancho de la imagen
            height: Alto de la imagen
            style: Estilo de la imagen
            additional_params: Parámetros adicionales
        
        Returns:
            Dict con información de la imagen generada
        """
        
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
        }
        
        if style:
            payload["style"] = style
        
        if additional_params:
            payload.update(additional_params)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/generate",
                headers=self.headers,
                json=payload,
                timeout=120.0  # 2 minutos de timeout
            )
            
            response.raise_for_status()
            return response.json()
    
    async def get_generation_status(self, generation_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado de una generación en progreso
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/generations/{generation_id}",
                headers=self.headers
            )
            
            response.raise_for_status()
            return response.json()
    
    async def download_image(self, image_url: str) -> bytes:
        """
        Descarga una imagen generada
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response.raise_for_status()
            return response.content


# Singleton instance
higgsfield_service = HiggsfieldService()
