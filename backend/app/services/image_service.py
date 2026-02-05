"""
Image Generation Service
Servicio para generar imágenes usando Higgsfield AI
"""
import httpx
from typing import Dict, Any, Optional
import asyncio

from app.core.config import settings


class ImageService:
    """Servicio para generación de imágenes con Higgsfield AI"""
    
    def __init__(self):
        self.api_key_id = settings.HIGGSFIELD_API_KEY_ID
        self.api_key_secret = settings.HIGGSFIELD_API_KEY_SECRET
        self.api_url = "https://platform.higgsfield.ai"
        self.headers = {
            "Authorization": f"Key {self.api_key_id}:{self.api_key_secret}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 768,
        style: Optional[str] = None,
        model: str = "higgsfield-ai/soul/standard"  # Modelo flagship de Higgsfield
    ) -> Dict[str, Any]:
        """
        Genera una imagen usando Higgsfield AI
        
        Args:
            prompt: Descripción de la imagen a generar
            width: Ancho de la imagen
            height: Alto de la imagen
            style: Estilo de la imagen (se añade al prompt)
            model: Modelo a usar (higgsfield-ai/soul/standard por defecto)
        
        Returns:
            Dict con información de la imagen generada incluyendo URL
        """
        
        # Construir el prompt completo
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style"
        
        # Calcular aspect_ratio y resolution
        aspect_ratio = f"{width}:{height}"
        if width == 1920 and height == 1080:
            aspect_ratio = "16:9"
        elif width == 1024 and height == 768:
            aspect_ratio = "4:3"
        elif width == 1024 and height == 1024:
            aspect_ratio = "1:1"
        
        resolution = "720p"
        if max(width, height) >= 1920:
            resolution = "1080p"
        
        payload = {
            "prompt": full_prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution
        }
        
        async with httpx.AsyncClient(timeout=180.0) as client:
            # Iniciar la generación - sistema asíncrono de Higgsfield
            response = await client.post(
                f"{self.api_url}/{model}",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code not in [200, 201, 202]:
                error_text = response.text
                print(f"Higgsfield Error {response.status_code}: {error_text}")
                raise Exception(f"Higgsfield Error: {response.status_code} - {error_text}")
            
            result = response.json()
            print(f"Higgsfield Response: {result}")
            
            # Obtener el request_id y esperar el resultado
            request_id = result.get("request_id")
            status_url = result.get("status_url")
            
            if not request_id:
                raise Exception("No request_id returned from Higgsfield API")
            
            # Esperar a que se complete la generación
            return await self._wait_for_result(client, request_id, status_url)
    
    async def _wait_for_result(
        self, 
        client: httpx.AsyncClient, 
        request_id: str,
        status_url: Optional[str] = None,
        max_attempts: int = 60
    ) -> Dict[str, Any]:
        """Espera el resultado de una generación asíncrona de Higgsfield"""
        
        # Construir la URL de status si no se proporciona
        if not status_url:
            status_url = f"{self.api_url}/requests/{request_id}/status"
        
        for attempt in range(max_attempts):
            await asyncio.sleep(3)  # Esperar 3 segundos entre cada check
            
            response = await client.get(
                status_url,
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                status = result.get("status", "").lower()
                
                print(f"Generation status: {status} (attempt {attempt + 1}/{max_attempts})")
                
                if status == "completed":
                    # La generación está completa
                    images = result.get("images", [])
                    if images and len(images) > 0:
                        return {
                            "success": True,
                            "image_url": images[0].get("url"),
                            "request_id": request_id,
                            "data": result
                        }
                    
                    # Verificar si hay video en lugar de imagen
                    video = result.get("video")
                    if video and video.get("url"):
                        return {
                            "success": True,
                            "video_url": video.get("url"),
                            "request_id": request_id,
                            "data": result
                        }
                    
                    return {
                        "success": True,
                        "request_id": request_id,
                        "data": result
                    }
                
                elif status in ["failed", "nsfw"]:
                    error_msg = f"Generation failed with status: {status}"
                    if status == "nsfw":
                        error_msg = "Content failed moderation checks (NSFW)"
                    raise Exception(error_msg)
                
                elif status in ["queued", "in_progress"]:
                    # Todavía procesando, continuar esperando
                    continue
                
                else:
                    # Estado desconocido
                    print(f"Unknown status: {status}")
                    continue
            
            else:
                print(f"Status check error: {response.status_code}")
        
        raise Exception("Generation timeout - max attempts reached")
    
    async def check_available_models(self) -> Dict[str, Any]:
        """Lista los modelos disponibles para generación de imágenes"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/models",
                headers=self.headers
            )
            return response.json()
