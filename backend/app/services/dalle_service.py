"""
DALL-E Image Service
Servicio para generar imágenes usando OpenAI DALL-E
"""
import httpx
from typing import Dict, Any, Optional

from app.core.config import settings


class DalleService:
    """Servicio para generación de imágenes con OpenAI DALL-E"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        style: Optional[str] = None,
        model: str = "dall-e-2",  # Usando DALL-E 2 por defecto (más estable)
        quality: str = "standard"  # "standard" o "hd"
    ) -> Dict[str, Any]:
        """
        Genera una imagen usando OpenAI DALL-E 3
        
        Args:
            prompt: Descripción de la imagen a generar
            width: Ancho de la imagen (DALL-E 3 soporta 1024x1024, 1792x1024, 1024x1792)
            height: Alto de la imagen
            style: Estilo de la imagen (se añade al prompt)
            model: Modelo a usar (dall-e-3 o dall-e-2)
            quality: Calidad (standard o hd)
        
        Returns:
            Dict con información de la imagen generada incluyendo URL
        """
        
        # Construir el prompt completo
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style, cinematic lighting, high quality"
        
        # DALL-E 2 soporta: 256x256, 512x512, 1024x1024
        # DALL-E 3 soporta: 1024x1024, 1792x1024, 1024x1792
        if model == "dall-e-3":
            # Elegir el tamaño más cercano soportado
            if width > height:
                size = "1792x1024"
            elif height > width:
                size = "1024x1792"
            else:
                size = "1024x1024"
        else:  # dall-e-2
            size = "1024x1024"  # Mejor calidad para DALL-E 2
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "n": 1,
            "size": size
        }
        
        # Solo DALL-E 3 soporta el parámetro quality
        if model == "dall-e-3":
            payload["quality"] = quality
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.api_url}/images/generations",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                error_text = response.text
                print(f"DALL-E Error {response.status_code}: {error_text}")
                raise Exception(f"DALL-E Error: {response.status_code} - {error_text}")
            
            result = response.json()
            print(f"DALL-E Response: Generated image successfully")
            
            # DALL-E retorna la URL directamente
            if "data" in result and len(result["data"]) > 0:
                return {
                    "success": True,
                    "image_url": result["data"][0].get("url"),
                    "revised_prompt": result["data"][0].get("revised_prompt"),
                    "data": result
                }
            
            raise Exception("No image data in response")
