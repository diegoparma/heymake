"""
Gemini Image Service (Nano Banana)
Servicio para generación de imágenes usando Google Gemini API
"""
import httpx
from typing import Optional, Dict, Any
from app.core.config import settings


class GeminiImageService:
    """Servicio para generar imágenes con Google Gemini (Nano Banana)"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_AI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        # Modelo recomendado: gemini-2.5-flash-image o gemini-3-pro-image-preview
        self.model = "gemini-3-pro-image-preview"
    
    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 768,
        style: Optional[str] = None,
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        Genera una imagen usando Gemini
        
        Args:
            prompt: El texto descriptivo de la imagen
            width: Ancho de la imagen (no usado directamente, se usa aspect_ratio)
            height: Alto de la imagen (no usado directamente, se usa aspect_ratio)
            style: Estilo opcional (no aplicado en Gemini por ahora)
            aspect_ratio: Relación de aspecto (1:1, 16:9, 9:16, etc.)
        
        Returns:
            Dict con success, image_url y data
        """
        
        if not self.api_key:
            return {
                "success": False,
                "error": "Google AI API key not configured"
            }
        
        # Ajustar aspect ratio basado en dimensiones
        if width == height:
            aspect_ratio = "1:1"
        elif width > height:
            aspect_ratio = "16:9"
        else:
            aspect_ratio = "9:16"
        
        url = f"{self.base_url}/models/{self.model}:generateContent"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Construir el payload según la API de Gemini
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 1.0,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
                "responseModalities": ["image"]
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=payload,
                    params={"key": self.api_key}
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.text else {}
                    print(f"Gemini API Error {response.status_code}: {error_data}")
                    return {
                        "success": False,
                        "error": f"Gemini API error: {response.status_code}",
                        "details": error_data
                    }
                
                data = response.json()
                print(f"Gemini Response: {data}")
                
                # Extraer la imagen del response
                # La estructura de respuesta de Gemini incluye la imagen en inlineData
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "inlineData" in part:
                                # La imagen viene como base64 en inlineData
                                mime_type = part["inlineData"].get("mimeType", "image/jpeg")
                                base64_data = part["inlineData"].get("data", "")
                                
                                # Convertir base64 a data URL
                                image_url = f"data:{mime_type};base64,{base64_data}"
                                
                                return {
                                    "success": True,
                                    "image_url": image_url,
                                    "mime_type": mime_type,
                                    "data": data
                                }
                
                # Si no se encontró imagen en la respuesta
                return {
                    "success": False,
                    "error": "No image found in Gemini response",
                    "data": data
                }
                
        except httpx.TimeoutException:
            print("Gemini API timeout")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
