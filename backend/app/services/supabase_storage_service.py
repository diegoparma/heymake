"""
Supabase Storage Service
Servicio para gestión de archivos en Supabase Storage
"""
import httpx
import base64
from typing import Optional
from app.core.config import settings

class SupabaseStorageService:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.anon_key = settings.SUPABASE_ANON_KEY
        self.service_key = settings.SUPABASE_SERVICE_KEY
        self.bucket = "heymake-images"
        self.headers = {
            "apikey": self.service_key or self.anon_key,
            "Authorization": f"Bearer {self.service_key or self.anon_key}"
        }
        # Crear bucket si no existe
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Crear el bucket si no existe"""
        url = f"{self.supabase_url}/storage/v1/bucket/{self.bucket}"
        with httpx.Client() as client:
            response = client.get(url, headers=self.headers, timeout=10)
            if response.status_code == 404:
                create_url = f"{self.supabase_url}/storage/v1/bucket"
                create_data = {
                    "name": self.bucket,
                    "public": True,
                    "file_size_limit": 52428800,
                    "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"],
                }
                create_response = client.post(create_url, headers=self.headers, json=create_data, timeout=10)
                if create_response.status_code in (200, 201):
                    print(f"✅ Bucket '{self.bucket}' creado en Supabase")
                else:
                    print(f"❌ Error creando bucket: {create_response.text}")
            elif response.status_code == 200:
                print(f"✅ Bucket '{self.bucket}' ya existe en Supabase")

    async def upload_image_from_url(self, image_url: str, filename: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code != 200:
                return None
            data = response.content
            return await self._upload_bytes(data, filename)

    async def upload_image_from_base64(self, base64_data: str, filename: str) -> Optional[str]:
        try:
            header, encoded = base64_data.split(",", 1)
            data = base64.b64decode(encoded)
            return await self._upload_bytes(data, filename)
        except Exception:
            return None

    async def _upload_bytes(self, data: bytes, filename: str) -> Optional[str]:
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{filename}"
        # Inferimos mime desde la extensión para cumplir con allowed_mime_types
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        ext = filename.lower()[filename.rfind("."):] if "." in filename else ""
        content_type = mime_map.get(ext, "image/png")
        request_headers = {
            **self.headers,
            "x-upsert": "true",
            "Content-Type": content_type,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=request_headers, content=data)
            if response.status_code not in (200, 201):
                print(f"❌ Supabase upload failed: {response.status_code} {response.text}")
                return None
        return self.get_public_url(filename)

    def get_public_url(self, filename: str) -> str:
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{filename}"

    async def delete_image(self, filename: str) -> bool:
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{filename}"
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers)
            return response.status_code == 200
