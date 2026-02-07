"""
Gemini Image Service
Servicio para generación de imágenes usando Google Gemini API
Soporta múltiples modelos con fallback automático
"""
import httpx
from typing import Optional, Dict, Any, List
from app.core.config import settings


class GeminiImageService:
    """Servicio para generar imágenes con Google Gemini"""
    
    # Lista de modelos en orden de preferencia para generación de imagen
    IMAGE_MODELS = [
        {"id": "gemini-2.0-flash-exp-image-generation", "modalities": ["TEXT", "IMAGE"]},
        {"id": "gemini-2.5-flash-image", "modalities": ["IMAGE"]},
        {"id": "gemini-3-pro-image-preview", "modalities": ["IMAGE"]},
        {"id": "nano-banana-pro-preview", "modalities": ["IMAGE"]},
    ]
    
    def __init__(self):
        self.api_key = settings.GOOGLE_AI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 768,
        style: Optional[str] = None,
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        Genera una imagen usando Gemini, intentando múltiples modelos con fallback.
        """
        
        if not self.api_key:
            return {
                "success": False,
                "error": "Google AI API key no configurada",
                "error_code": "no_api_key"
            }
        
        last_error = None
        
        for model_config in self.IMAGE_MODELS:
            model_id = model_config["id"]
            modalities = model_config["modalities"]
            
            print(f"🎨 Gemini: Intentando con modelo {model_id}...")
            result = await self._try_model(model_id, modalities, prompt, style)
            
            if result["success"]:
                return result
            
            error_code = result.get("error_code", "")
            last_error = result
            
            # Si es quota exhausted, probar siguiente modelo
            if error_code == "quota_exhausted":
                print(f"⚠️ Gemini: Quota agotada en {model_id}, probando siguiente modelo...")
                continue
            
            # Si es NSFW o error de contenido, no tiene sentido probar otro modelo
            if error_code in ("nsfw", "safety_blocked"):
                return result
            
            # Para otros errores, seguir intentando
            print(f"⚠️ Gemini: Error en {model_id}: {result.get('error')}, probando siguiente...")
            continue
        
        # Si ningún modelo funcionó
        if last_error and last_error.get("error_code") == "quota_exhausted":
            return {
                "success": False,
                "error": "Quota agotada en todos los modelos de Gemini. Se alcanzó el límite diario del free tier.",
                "error_code": "quota_exhausted"
            }
        
        return last_error or {
            "success": False,
            "error": "No se pudo generar la imagen con ningún modelo de Gemini",
            "error_code": "all_models_failed"
        }
    
    async def _try_model(
        self,
        model_id: str,
        modalities: List[str],
        prompt: str,
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Intenta generar imagen con un modelo específico"""
        
        url = f"{self.base_url}/models/{model_id}:generateContent"
        
        # Construir prompt con estilo
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}. Style: {style}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": full_prompt
                }]
            }],
            "generationConfig": {
                "temperature": 1.0,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
                "responseModalities": modalities
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    params={"key": self.api_key}
                )
                
                if response.status_code == 429:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("error", {}).get("message", "")
                    print(f"❌ Gemini: Quota agotada en {model_id}")
                    return {
                        "success": False,
                        "error": f"Quota agotada en modelo {model_id}: {error_msg[:150]}",
                        "error_code": "quota_exhausted"
                    }
                
                if response.status_code == 400:
                    error_data = response.json() if response.text else {}
                    error_msg = error_data.get("error", {}).get("message", "")
                    return {
                        "success": False,
                        "error": f"Gemini {model_id}: {error_msg[:200]}",
                        "error_code": "bad_request"
                    }
                
                if response.status_code == 503:
                    return {
                        "success": False,
                        "error": f"Modelo {model_id} sobrecargado, intentá más tarde",
                        "error_code": "overloaded"
                    }
                
                if response.status_code != 200:
                    error_data = response.json() if response.text else {}
                    print(f"❌ Gemini API Error {response.status_code}: {error_data}")
                    return {
                        "success": False,
                        "error": f"Gemini API error: {response.status_code}",
                        "error_code": "api_error",
                        "details": error_data
                    }
                
                data = response.json()
                
                # Verificar si el contenido fue bloqueado por safety
                if "candidates" in data and len(data["candidates"]) > 0:
                    candidate = data["candidates"][0]
                    finish_reason = candidate.get("finishReason", "")
                    
                    if finish_reason == "SAFETY":
                        return {
                            "success": False,
                            "error": "La imagen fue bloqueada por el filtro de seguridad de Google. Intentá con otro prompt.",
                            "error_code": "safety_blocked"
                        }
                    
                    if finish_reason == "NO_IMAGE":
                        return {
                            "success": False,
                            "error": f"El modelo {model_id} no pudo generar una imagen para este prompt",
                            "error_code": "no_image"
                        }
                    
                    if "content" in candidate and "parts" in candidate["content"]:
                        for part in candidate["content"]["parts"]:
                            if "inlineData" in part:
                                mime_type = part["inlineData"].get("mimeType", "image/jpeg")
                                base64_data = part["inlineData"].get("data", "")
                                
                                image_url = f"data:{mime_type};base64,{base64_data}"
                                
                                print(f"✅ Gemini: Imagen generada con {model_id}")
                                return {
                                    "success": True,
                                    "image_url": image_url,
                                    "mime_type": mime_type,
                                    "model": model_id,
                                    "data": {}
                                }
                
                # No se encontró imagen en la respuesta
                return {
                    "success": False,
                    "error": f"No se encontró imagen en la respuesta de {model_id}",
                    "error_code": "no_image"
                }
                
        except httpx.TimeoutException:
            print(f"❌ Gemini: Timeout con {model_id}")
            return {
                "success": False,
                "error": f"Timeout con modelo {model_id}",
                "error_code": "timeout"
            }
        except Exception as e:
            print(f"❌ Gemini: Error con {model_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_code": "unexpected_error"
            }
