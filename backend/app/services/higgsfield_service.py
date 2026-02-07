"""
Higgsfield Service
Servicio para interactuar con la API de Higgsfield (platform.higgsfield.ai)
Usa patrón async queue: POST → queue → poll status hasta completed/failed
Docs: https://docs.higgsfield.ai/how-to/introduction
"""
import httpx
import asyncio
from typing import Dict, Any, Optional

from app.core.config import settings


class HiggsfieldService:
    """Servicio para generación de imágenes con Higgsfield"""
    
    # Modelo por defecto para text-to-image
    DEFAULT_MODEL = "higgsfield-ai/soul/standard"
    
    def __init__(self):
        self.api_key_id = settings.HIGGSFIELD_API_KEY_ID
        self.api_key_secret = settings.HIGGSFIELD_API_KEY_SECRET
        self.base_url = "https://platform.higgsfield.ai"
        self.headers = {
            "Authorization": f"Key {self.api_key_id}:{self.api_key_secret}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 768,
        style: Optional[str] = None,
        model: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Genera una imagen usando Higgsfield.
        
        Flujo:
        1. POST al modelo → recibe request_id + status_url
        2. Poll status_url hasta que esté completed/failed/nsfw
        3. Retorna la URL de la imagen
        """
        model_id = model or self.DEFAULT_MODEL
        url = f"{self.base_url}/{model_id}"
        
        # Calcular aspect ratio basado en dimensiones
        if width == height:
            aspect_ratio = "1:1"
        elif width > height:
            aspect_ratio = "16:9"
        else:
            aspect_ratio = "9:16"
        
        # Agregar estilo al prompt si se proporcionó
        full_prompt = f"{prompt}, {style} style" if style else prompt
        
        payload = {
            "prompt": full_prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": "720p"
        }
        
        if additional_params:
            payload.update(additional_params)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 1. Enviar request de generación
                print(f"🎨 Higgsfield: POST {url}")
                response = await client.post(url, headers=self.headers, json=payload)
                
                if response.status_code == 403:
                    error_detail = response.json().get("detail", "")
                    if "Not enough credits" in error_detail:
                        print(f"❌ Higgsfield: Sin créditos")
                        return {
                            "success": False,
                            "error": "No hay créditos disponibles en Higgsfield. Recargá créditos en https://cloud.higgsfield.ai",
                            "error_code": "no_credits"
                        }
                    return {
                        "success": False,
                        "error": f"Acceso denegado: {error_detail}",
                        "error_code": "forbidden"
                    }
                
                if response.status_code == 404:
                    return {
                        "success": False,
                        "error": f"Modelo '{model_id}' no encontrado en Higgsfield",
                        "error_code": "model_not_found"
                    }
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Higgsfield API error: {response.status_code} - {response.text[:200]}",
                        "error_code": "api_error"
                    }
                
                data = response.json()
                request_id = data.get("request_id")
                status_url = data.get("status_url")
                
                if not status_url:
                    return {
                        "success": False,
                        "error": "No se recibió status_url de Higgsfield",
                        "error_code": "invalid_response"
                    }
                
                print(f"📋 Higgsfield: Request {request_id} queued, polling...")
                
                # 2. Poll status hasta completado (max 120 segundos)
                max_polls = 40  # 40 * 3s = 120s
                for i in range(max_polls):
                    await asyncio.sleep(3)
                    
                    status_response = await client.get(status_url, headers=self.headers)
                    
                    if status_response.status_code != 200:
                        print(f"⚠️ Higgsfield: Error polling status: {status_response.status_code}")
                        continue
                    
                    status_data = status_response.json()
                    current_status = status_data.get("status")
                    
                    print(f"  [{i+1}/{max_polls}] Status: {current_status}")
                    
                    if current_status == "completed":
                        images = status_data.get("images", [])
                        if images:
                            image_url = images[0].get("url")
                            if image_url:
                                print(f"✅ Higgsfield: Imagen generada: {image_url[:100]}")
                                return {
                                    "success": True,
                                    "image_url": image_url,
                                    "url": image_url,
                                    "request_id": request_id,
                                    "data": status_data
                                }
                        return {
                            "success": False,
                            "error": "Generación completada pero no se recibió URL de imagen",
                            "error_code": "no_image_url"
                        }
                    
                    elif current_status == "nsfw":
                        print(f"🚫 Higgsfield: Contenido NSFW detectado")
                        return {
                            "success": False,
                            "error": "El contenido fue rechazado por el filtro de seguridad (NSFW). Intentá con otro prompt.",
                            "error_code": "nsfw"
                        }
                    
                    elif current_status == "failed":
                        print(f"❌ Higgsfield: Generación fallida")
                        return {
                            "success": False,
                            "error": "La generación falló en Higgsfield. Intentá de nuevo.",
                            "error_code": "generation_failed"
                        }
                
                # Timeout
                return {
                    "success": False,
                    "error": "Timeout esperando generación de Higgsfield (120s)",
                    "error_code": "timeout"
                }
                
        except httpx.TimeoutException:
            print("❌ Higgsfield: Connection timeout")
            return {
                "success": False,
                "error": "Timeout de conexión con Higgsfield",
                "error_code": "connection_timeout"
            }
        except Exception as e:
            print(f"❌ Higgsfield: Error inesperado: {e}")
            return {
                "success": False,
                "error": f"Error inesperado: {str(e)}",
                "error_code": "unexpected_error"
            }
    
    async def get_generation_status(self, request_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado de una generación en progreso
        """
        status_url = f"{self.base_url}/requests/{request_id}/status"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(status_url, headers=self.headers)
            if response.status_code != 200:
                return {"error": f"Status check failed: {response.status_code}"}
            return response.json()
    
    async def cancel_generation(self, request_id: str) -> Dict[str, Any]:
        """
        Cancela una generación que está en cola
        """
        cancel_url = f"{self.base_url}/requests/{request_id}/cancel"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(cancel_url, headers=self.headers)
            return {
                "cancelled": response.status_code == 202,
                "status_code": response.status_code
            }


# Singleton instance
higgsfield_service = HiggsfieldService()
