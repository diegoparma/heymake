"""
Storage Service
Servicio para gestión de archivos con Google Drive
"""
import os
import io
from pathlib import Path
from typing import Optional, Dict, Any
import uuid
import pickle

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError


from app.core.config import settings
from app.services.supabase_storage_service import SupabaseStorageService


class StorageService:
    """Servicio para almacenamiento de archivos en Google Drive"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self):
        # Normalizamos el provider para evitar problemas por espacios o mayúsculas
        self.provider = settings.STORAGE_PROVIDER.strip().lower()
        self.base_path = Path("uploads")
        self.drive_service = None
        self.folder_id = settings.GOOGLE_DRIVE_FOLDER_ID
        
        # Setup según el provider
        if self.provider == "local":
            self._setup_local()
        elif self.provider == "gdrive":
            self._setup_google_drive_service_account()
        elif self.provider == "supabase":
            self.supabase = SupabaseStorageService()

    async def upload_image_from_url(self, image_url: str, filename: str) -> str:
        """Sube una imagen a Supabase a partir de una URL"""
        return await self.supabase.upload_image_from_url(image_url, filename)

    async def upload_image_from_base64(self, base64_data: str, filename: str) -> str:
        """Sube una imagen a Supabase a partir de datos base64"""
        return await self.supabase.upload_image_from_base64(base64_data, filename)

    async def delete_image_from_supabase(self, filename: str) -> bool:
        """Elimina una imagen del bucket de Supabase"""
        return await self.supabase.delete_image(filename)
    
    def _setup_local(self):
        """Setup para almacenamiento local"""
        self.base_path.mkdir(exist_ok=True)
        (self.base_path / "images").mkdir(exist_ok=True)
        (self.base_path / "videos").mkdir(exist_ok=True)
        (self.base_path / "audio").mkdir(exist_ok=True)
    
    def _setup_google_drive_service_account(self):
        """Setup para Google Drive API usando Service Account"""
        try:
            credentials_file = settings.GOOGLE_DRIVE_CREDENTIALS_FILE
            
            if not os.path.exists(credentials_file):
                print(f"⚠️  Warning: Service Account credentials file not found: {credentials_file}")
                return
            
            # Cargar credenciales de Service Account
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=self.SCOPES
            )
            
            # Build the service
            self.drive_service = build('drive', 'v3', credentials=credentials)
            print("✅ Google Drive service initialized (Service Account)")
            
        except Exception as e:
            print(f"❌ Error initializing Google Drive: {e}")
            self.drive_service = None
    
    async def save_file(
        self,
        file_content: bytes,
        filename: str,
        folder: str = "images",
        mime_type: str = "image/jpeg"
    ) -> Dict[str, str]:
        """
        Guarda un archivo
        """
        if self.provider == "local":
            return await self._save_local(file_content, filename, folder)
        elif self.provider == "gdrive":
            return await self._save_google_drive(file_content, filename, folder, mime_type)
        elif self.provider == "supabase":
            # Guardar en Supabase bucket
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            url = await self.supabase._upload_bytes(file_content, unique_filename)
            return {
                "file_id": unique_filename,
                "file_path": url,
                "web_view_link": url,
            }
        else:
            raise ValueError(f"Unsupported storage provider: {self.provider}")
    
    async def _save_local(
        self,
        file_content: bytes,
        filename: str,
        folder: str
    ) -> Dict[str, str]:
        """Guarda archivo localmente"""
        
        # Generar nombre único
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = self.base_path / folder / unique_filename
        
        # Guardar archivo
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return {
            "file_id": unique_filename,
            "file_path": str(file_path),
            "web_view_link": f"file://{file_path}",
        }
    
    async def _save_google_drive(
        self,
        file_content: bytes,
        filename: str,
        folder: str,
        mime_type: str
    ) -> Dict[str, str]:
        """Guarda archivo en Google Drive"""
        
        if not self.drive_service:
            raise Exception("Google Drive service not initialized")
        
        try:
            # Metadata del archivo
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            # Crear media upload desde bytes
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type,
                resumable=True
            )
            
            # Subir archivo con soporte para Shared Drives
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, webContentLink',
                supportsAllDrives=True
            ).execute()
            
            print(f"📁 File uploaded to Drive: {file.get('name')} (ID: {file.get('id')})")
            
            return {
                "file_id": file.get('id'),
                "file_path": file.get('webContentLink', ''),
                "web_view_link": file.get('webViewLink', ''),
            }
            
        except HttpError as error:
            raise Exception(f"Error uploading to Google Drive: {error}")
            
        except HttpError as error:
            raise Exception(f"Error uploading to Google Drive: {error}")
    
    async def get_file(self, file_id: str) -> bytes:
        """
        Obtiene un archivo
        
        Args:
            file_id: ID del archivo (path local o Google Drive ID)
        
        Returns:
            Contenido del archivo en bytes
        """
        
        if self.provider == "local":
            with open(file_id, "rb") as f:
                return f.read()
        elif self.provider == "gdrive":
            return await self._get_from_google_drive(file_id)
        elif self.provider == "supabase":
            # Descargar desde Supabase Storage
            url = self.supabase.get_public_url(file_id)
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.content
        else:
            raise NotImplementedError(f"Get file not implemented for {self.provider}")
    
    async def _get_from_google_drive(self, file_id: str) -> bytes:
        """Descarga archivo de Google Drive"""
        
        if not self.drive_service:
            raise Exception("Google Drive service not initialized")
        
        try:
            request = self.drive_service.files().get_media(fileId=file_id)
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_buffer.seek(0)
            return file_buffer.read()
            
        except HttpError as error:
            raise Exception(f"Error downloading from Google Drive: {error}")
    
    async def delete_file(self, file_id: str) -> bool:
        """
        Elimina un archivo
        
        Args:
            file_id: ID del archivo (path local o Google Drive ID)
        
        Returns:
            True si se eliminó exitosamente
        """
        
        if self.provider == "local":
            try:
                os.remove(file_id)
                return True
            except Exception:
                return False
        elif self.provider == "gdrive":
            return await self._delete_from_google_drive(file_id)
        elif self.provider == "supabase":
            return await self.supabase.delete_image(file_id)
        else:
            raise NotImplementedError(f"Delete file not implemented for {self.provider}")
    
    async def _delete_from_google_drive(self, file_id: str) -> bool:
        """Elimina archivo de Google Drive"""
        
        if not self.drive_service:
            raise Exception("Google Drive service not initialized")
        
        try:
            self.drive_service.files().delete(fileId=file_id).execute()
            return True
        except HttpError:
            return False
    
    def get_view_link(self, file_id: str) -> str:
        """
        Obtiene el link para visualizar un archivo
        
        Args:
            file_id: ID del archivo
        
        Returns:
            URL para visualizar el archivo
        """
        
        if self.provider == "gdrive":
            return f"https://drive.google.com/file/d/{file_id}/view"
        elif self.provider == "supabase":
            return self.supabase.get_public_url(file_id)
        else:
            return f"file://{file_id}"


# Singleton instance
storage_service = StorageService()
