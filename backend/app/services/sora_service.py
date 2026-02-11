"""
Sora Service (OpenAI text-to-video / image-to-video)
Nota: Usa la misma OPENAI_API_KEY. Endpoints y payloads pueden variar según el acceso temprano.
"""
import asyncio
from typing import Dict, Any, Optional

import httpx

from app.core.config import settings


class SoraService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.SORA_MODEL
        self.api_base = settings.SORA_API_BASE.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_from_text(
        self,
        prompt: str,
        duration: float = 5.0,
        aspect_ratio: str = "16:9",
    ) -> Dict[str, Any]:
        """Genera video desde texto usando Sora (OpenAI)."""
        if not self.api_key:
            return {"success": False, "error": "OPENAI_API_KEY no configurada"}

        payload = {
            "model": self.model,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
        }

        return await self._post_generation(payload)

    async def animate_image(
        self,
        image_url: str,
        duration: float = 5.0,
        motion_type: str = "auto",
        additional_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Anima una imagen si el endpoint de Sora lo soporta."""
        if not self.api_key:
            return {"success": False, "error": "OPENAI_API_KEY no configurada"}

        payload = {
            "model": self.model,
            "prompt": f"Animate this image with motion: {motion_type}",
            "image_url": image_url,
            "duration": duration,
        }
        if additional_params:
            payload.update(additional_params)

        return await self._post_generation(payload)

    async def _post_generation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.api_base}/videos"
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, json=payload, headers=self.headers)

        if response.status_code >= 400:
            return {
                "success": False,
                "error": f"Sora API error {response.status_code}",
                "details": response.text,
            }

        data = response.json()
        # Intentar extraer URL y task_id de respuestas comunes
        video_url = (
            data.get("video_url")
            or data.get("url")
            or (data.get("data") or [{}])[0].get("url")
            or (data.get("output") or {}).get("url")
        )
        task_id = data.get("id") or data.get("task_id") or data.get("job_id")

        result: Dict[str, Any] = {
            "success": True,
            "status": data.get("status") or ("completed" if video_url else "processing"),
            "task_id": task_id,
            "video_url": video_url,
            "raw": data,
        }
        return result

    async def get_animation_status(self, task_id: str) -> Dict[str, Any]:
        """Consulta el estado de un job de Sora si el endpoint lo soporta."""
        url = f"{self.api_base}/videos/{task_id}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=self.headers)

        if response.status_code >= 400:
            return {"status": "error", "error": response.text}

        data = response.json()
        video_url = data.get("video_url") or data.get("url") or (data.get("data") or [{}])[0].get("url")
        return {
            "status": data.get("status", "processing"),
            "video_url": video_url,
            "raw": data,
        }


sora_service = SoraService()
