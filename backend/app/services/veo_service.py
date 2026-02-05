"""
Google Veo Service
Servicio para generación de videos usando Google Veo 3.1
Documentación: https://ai.google.dev/gemini-api/docs/video
"""
from google import genai
from google.genai import types
from typing import Dict, Any, Optional
import asyncio
import time
from pathlib import Path
import base64

from app.core.config import settings


class VeoService:
    """Servicio para generación de videos con Google Veo 3.1"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_AI_API_KEY
        self.model = "veo-3.1-generate-preview"  # Veo 3.1 preview model
        self.client = genai.Client(api_key=self.api_key)
    
    async def animate_image(
        self,
        image_url: str,
        duration: float = 5.0,
        motion_type: str = "auto",
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Anima una imagen usando Google Veo 3.1
        
        Args:
            image_url: URL de la imagen a animar (puede ser local o HTTP)
            duration: Duración del video en segundos (4-8 segundos)
            motion_type: Tipo de movimiento (usado en el prompt)
            additional_params: Parámetros adicionales
        
        Returns:
            Dict con información del video generado
        """
        
        if not self.api_key:
            return {
                "success": False,
                "error": "Google AI API key not configured"
            }
        
        # Ajustar duración a valores válidos de Veo 3.1
        if duration <= 4:
            duration_seconds = 4
        elif duration <= 6:
            duration_seconds = 6
        else:
            duration_seconds = 8
        
        # Crear prompt basado en motion_type
        motion_prompts = {
            "auto": "Animate this image with natural, smooth cinematic movement. Add subtle depth and motion to bring the scene to life.",
            "zoom_in": "Slowly zoom into this image with smooth camera movement, revealing more detail as we move closer",
            "zoom_out": "Slowly zoom out from this image with smooth camera movement, revealing more of the surrounding scene",
            "pan_left": "Pan the camera slowly to the left across this scene with smooth cinematic movement",
            "pan_right": "Pan the camera slowly to the right across this scene with smooth cinematic movement",
            "tilt_up": "Tilt the camera slowly upward revealing more of the scene above",
            "tilt_down": "Tilt the camera slowly downward revealing more of the scene below"
        }
        
        prompt = motion_prompts.get(motion_type, motion_prompts["auto"])
        
        try:
            # Obtener la imagen local
            if image_url.startswith("http://localhost") or image_url.startswith("file://"):
                # Imagen local
                local_path = image_url.replace("http://localhost:8000/api/v1/assets/image/", "")
                file_path = Path("uploads/images") / local_path
                
                if not file_path.exists():
                    return {
                        "success": False,
                        "error": f"Local image not found: {file_path}"
                    }
            else:
                return {
                    "success": False,
                    "error": "Only local images are supported for now"
                }
            
            print(f"🎬 Starting Veo 3.1 animation (duration: {duration_seconds}s, motion: {motion_type})")
            print(f"🖼️  Image path: {file_path}")
            
            # Leer imagen y convertir a base64
            with open(file_path, "rb") as f:
                image_bytes = f.read()
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Crear objeto Image con base64
            image_obj = types.Image(
                image_bytes=image_b64,
                mime_type="image/png"
            )
            
            # Crear la configuración
            config_dict = {
                "durationSeconds": duration_seconds,
                "aspectRatio": "16:9",
                "personGeneration": "allow_adult"  # Requerido para image-to-video
            }
            
            if additional_params:
                config_dict.update(additional_params)
            
            config = types.GenerateVideosConfig(**config_dict)
            
            print(f"📦 Config: {config_dict}")
            
            # Llamar a la API usando el SDK
            # Nota: El SDK hace llamadas síncronas, así que lo ejecutamos en un thread separado
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_videos(
                    model=self.model,
                    prompt=prompt,
                    image=image_obj,  # Objeto Image con base64
                    config=config
                )
            )
            
            operation_name = operation.name
            
            print(f"✅ Veo 3.1 animation started: {operation_name}")
            
            return {
                "success": True,
                "task_id": operation_name,
                "status": "processing",
                "provider": "veo",
                "estimated_time": duration_seconds * 10  # Estimación: 10x la duración del video
            }
                
        except Exception as e:
            print(f"❌ Error animating with Veo 3.1: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def generate_from_text(
        self,
        prompt: str,
        duration: float = 5.0,
        aspect_ratio: str = "16:9"
    ) -> Dict[str, Any]:
        """
        Genera un video desde texto usando Google Veo 3.1
        
        Args:
            prompt: Descripción del video a generar
            duration: Duración del video en segundos (4, 6 o 8)
            aspect_ratio: Relación de aspecto (16:9 o 9:16)
        
        Returns:
            Dict con información del video generado
        """
        
        if not self.api_key:
            return {
                "success": False,
                "error": "Google AI API key not configured"
            }
        
        # Ajustar duración
        if duration < 5:
            duration_seconds = 4
        elif duration < 7:
            duration_seconds = 6
        else:
            duration_seconds = 8
        
        try:
            url = f"{self.base_url}/models/{self.model}:generateVideos"
            
            payload = {
                "prompt": prompt,
                "config": {
                    "durationSeconds": duration_seconds,
                    "aspectRatio": aspect_ratio,
                    "resolution": "720p"
                }
            }
            
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    params={"key": self.api_key},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.text else {}
                    return {
                        "success": False,
                        "error": f"Veo API error: {response.status_code}",
                        "details": error_data
                    }
                
                data = response.json()
                operation_name = data.get("name")
                
                if not operation_name:
                    return {
                        "success": False,
                        "error": "No operation name returned"
                    }
                
                return {
                    "success": True,
                    "task_id": operation_name,
                    "status": "processing"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_animation_status(self, task_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado de una operación de Veo 3.1
        
        Args:
            task_id: Nombre de la operación (operation name)
        
        Returns:
            Dict con el estado y URL del video si está completo
        """
        
        try:
            # Usar el SDK para obtener el estado de la operación
            loop = asyncio.get_event_loop()
            operation = await loop.run_in_executor(
                None,
                lambda: self.client.operations.get(
                    types.GenerateVideosOperation(name=task_id)
                )
            )
            
            # Verificar si está completo
            is_done = operation.done
            
            if not is_done:
                return {
                    "task_id": task_id,
                    "status": "processing",
                    "progress": "Video generation in progress"
                }
            
            # Verificar si hubo error
            if hasattr(operation, 'error') and operation.error:
                error_msg = str(operation.error)
                print(f"❌ Veo 3.1 generation failed: {error_msg}")
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": error_msg
                }
            
            # Extraer video de la respuesta
            if not hasattr(operation, 'response') or not operation.response:
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": "No response in completed operation"
                }
            
            generated_videos = operation.response.generated_videos
            
            if not generated_videos or len(generated_videos) == 0:
                # Verificar si fue filtrado por RAI
                if hasattr(operation.response, 'rai_media_filtered_count') and operation.response.rai_media_filtered_count:
                    reasons = operation.response.rai_media_filtered_reasons if hasattr(operation.response, 'rai_media_filtered_reasons') else []
                    error_msg = f"Video filtered by safety filters: {', '.join(reasons)}"
                    print(f"⚠️  {error_msg}")
                    return {
                        "task_id": task_id,
                        "status": "failed",
                        "error": error_msg
                    }
                
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": "No video generated"
                }
            
            video = generated_videos[0]
            video_file = video.video
            
            # Descargar y guardar el video localmente
            try:
                # El video_file es un objeto Video con uri
                video_uri = video_file.uri if hasattr(video_file, 'uri') else str(video_file)
                
                # Agregar API key al URI
                if '?' in video_uri:
                    video_uri_with_key = f"{video_uri}&key={self.api_key}"
                else:
                    video_uri_with_key = f"{video_uri}?key={self.api_key}"
                
                print(f"📥 Downloading Veo 3.1 video from: {video_uri}")
                
                # Descargar el video usando httpx directamente con API key
                loop = asyncio.get_event_loop()
                
                async def download_video():
                    async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
                        response = await client.get(video_uri_with_key)
                        if response.status_code == 200:
                            return response.content
                        else:
                            raise Exception(f"Failed to download video: {response.status_code}")
                
                video_bytes = await download_video()
                
                # Crear directorio de videos si no existe
                videos_dir = Path("uploads/videos")
                videos_dir.mkdir(parents=True, exist_ok=True)
                
                # Generar nombre único para el video
                import uuid
                video_filename = f"veo_{uuid.uuid4().hex[:12]}.mp4"
                video_path = videos_dir / video_filename
                
                # Guardar el video localmente
                with open(video_path, "wb") as f:
                    f.write(video_bytes)
                
                # URL local para servir el video
                local_video_url = f"http://localhost:8000/api/v1/assets/video/{video_filename}"
                
                print(f"✅ Veo 3.1 video downloaded: {video_filename} ({len(video_bytes) / 1024 / 1024:.2f} MB)")
                
                return {
                    "task_id": task_id,
                    "status": "completed",
                    "video_url": local_video_url,
                    "provider": "veo",
                    "file_size": len(video_bytes)
                }
                
            except Exception as download_error:
                print(f"❌ Error downloading Veo 3.1 video: {download_error}")
                return {
                    "task_id": task_id,
                    "status": "failed",
                    "error": f"Failed to download video: {str(download_error)}"
                }
                
        except Exception as e:
            print(f"❌ Error checking Veo 3.1 status: {e}")
            import traceback
            traceback.print_exc()
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }
    
    async def wait_for_animation(
        self,
        task_id: str,
        max_wait: int = 360,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        Espera a que una animación se complete
        
        Args:
            task_id: ID de la operación
            max_wait: Tiempo máximo de espera en segundos (default: 6 minutos)
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
            elif status.get("status") == "error":
                raise Exception(f"Error checking status: {status.get('error')}")
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        raise TimeoutError(f"Animation did not complete within {max_wait} seconds")


# Singleton instance
veo_service = VeoService()
