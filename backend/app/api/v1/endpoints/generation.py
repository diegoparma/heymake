"""
Generation Endpoints
Endpoints para la generación de contenido con IA
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Dict, AsyncGenerator
import uuid
import json
import asyncio
from datetime import datetime

from app.core.database import get_turso_client
from app.schemas.generation import (
    ScriptAnalysisRequest,
    ScriptAnalysisResponse,
    ImageGenerationRequest,
    ImageGenerationResponse
)
from app.services.llm_service import LLMService

router = APIRouter()


@router.post("/analyze-script", response_model=ScriptAnalysisResponse)
async def analyze_script(request: ScriptAnalysisRequest):
    """
    Analizar un guión y generar escenas usando LLM
    """
    turso_client = get_turso_client()
    
    # Verificar que el proyecto existe
    result = await turso_client.execute(
        "SELECT id, title, style, reference_prompt, duration_target FROM projects WHERE id = ?",
        [request.project_id]
    )
    
    if not result or len(result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = result[0]
    
    # Analizar el guión con LLM
    llm_service = LLMService()
    scenes = await llm_service.analyze_script(
        script=request.script,
        style=project.get("style", "cinematic"),
        reference_prompt=project.get("reference_prompt"),
        duration_target=project.get("duration_target")
    )
    
    # Guardar las escenas en la base de datos
    for scene in scenes:
        scene_id = str(uuid.uuid4())
        await turso_client.execute(
            """INSERT INTO scenes (
                id, project_id, order_index, title, description,
                dialogue, image_prompt, duration, notes, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                scene_id,
                request.project_id,
                scene.order,
                scene.title,
                scene.description,
                scene.dialogue,
                scene.image_prompt,
                scene.duration,
                scene.notes,
                "pending",
                datetime.utcnow().isoformat()
            ]
        )
    
    # Actualizar el estado del proyecto
    await turso_client.execute(
        "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
        ["scenes_ready", datetime.utcnow().isoformat(), request.project_id]
    )
    
    return ScriptAnalysisResponse(
        project_id=request.project_id,
        scenes=scenes,
        total_scenes=len(scenes),
        estimated_duration=sum(s.duration for s in scenes)
    )


@router.post("/generate-images/{project_id}")
async def generate_images(
    project_id: str,
    background_tasks: BackgroundTasks,
    provider: str = "dalle"  # "dalle", "aimlapi", "higgsfield", "gemini"
):
    """
    Generar imágenes para todas las escenas del proyecto.
    Soporta DALL-E (OpenAI), AIMLAPI (Flux), Higgsfield o Gemini (Nano Banana) como proveedores.
    """
    from app.services.image_service import ImageService
    from app.services.higgsfield_service import HiggsfieldService
    from app.services.dalle_service import DalleService
    from app.services.gemini_image_service import GeminiImageService
    from app.services.storage_service import StorageService
    import uuid
    from datetime import datetime
    
    print(f"🎨 Using image provider: {provider}")
    
    turso_client = get_turso_client()
    
    # Verificar que el proyecto existe
    project_result = await turso_client.execute(
        "SELECT id, title, style FROM projects WHERE id = ?",
        [project_id]
    )
    
    if not project_result or len(project_result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = project_result[0]
    
    # Obtener las escenas del proyecto
    scenes_result = await turso_client.execute(
        "SELECT id, image_prompt, title, order_index FROM scenes WHERE project_id = ? ORDER BY order_index",
        [project_id]
    )
    
    if not scenes_result or len(scenes_result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No scenes found for this project"
        )
    
    # Seleccionar el servicio según el proveedor
    if provider == "higgsfield":
        image_generator = HiggsfieldService()
        print("📸 Using Higgsfield for image generation")
    elif provider == "aimlapi":
        image_generator = ImageService()
        print("📸 Using AIMLAPI (Flux) for image generation")
    elif provider == "gemini":
        image_generator = GeminiImageService()
        print("📸 Using Google Gemini (Nano Banana) for image generation")
    else:  # dalle (default)
        image_generator = DalleService()
        print("📸 Using OpenAI DALL-E for image generation")
    
    storage = StorageService()
    generated_count = 0
    
    for scene in scenes_result:
        try:
            print(f"🎨 Generating image for scene {scene['order_index']}: {scene['title']}")
            
            # Generar imagen con el proveedor seleccionado
            result = await image_generator.generate_image(
                prompt=scene["image_prompt"],
                width=1024,
                height=768,
                style=project.get("style", "cinematic")
            )
            
            print(f"✅ Image generated: {result}")
            
            # Obtener la URL de la imagen
            image_url = result.get("image_url") or result.get("url")
            
            if not image_url:
                print(f"❌ No image URL returned for scene {scene['order_index']}")
                continue
            
            # Procesar imagen: guardar localmente o usar URL externa
            final_url = None
            import base64
            from pathlib import Path
            
            # Crear directorio de imágenes si no existe
            images_dir = Path("uploads/images")
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # Nombre de archivo único
            filename = f"scene_{project_id[:8]}_{scene['order_index']:02d}_{scene['id'][:8]}.png"
            file_path = images_dir / filename
            
            # Si es data URL (Gemini), decodificar y guardar localmente
            if image_url.startswith("data:"):
                try:
                    # Decodificar base64
                    header, encoded = image_url.split(",", 1)
                    image_bytes = base64.b64decode(encoded)
                    
                    # Guardar archivo localmente
                    with open(file_path, "wb") as f:
                        f.write(image_bytes)
                    
                    # URL completa (accesible desde frontend)
                    final_url = f"http://localhost:8000/api/v1/assets/image/{filename}"
                    print(f"💾 Image saved locally: {file_path} ({len(image_bytes)} bytes)")
                    
                except Exception as e:
                    print(f"❌ Error saving image locally: {e}")
                    continue
                    
            # Si es URL HTTP (DALL-E), descargar y guardar localmente
            elif image_url.startswith("http"):
                try:
                    import httpx
                    
                    async with httpx.AsyncClient(timeout=30.0) as http_client:
                        img_response = await http_client.get(image_url)
                        if img_response.status_code == 200:
                            image_bytes = img_response.content
                            
                            # Guardar archivo localmente
                            with open(file_path, "wb") as f:
                                f.write(image_bytes)
                            
                            # URL completa (accesible desde frontend)
                            final_url = f"http://localhost:8000/api/v1/assets/image/{filename}"
                            print(f"💾 Image downloaded and saved: {file_path} ({len(image_bytes)} bytes)")
                        else:
                            print(f"⚠️ Failed to download image: {img_response.status_code}")
                            continue
                            
                except Exception as e:
                    print(f"❌ Error downloading image: {e}")
                    continue
            
            if not final_url:
                print(f"❌ Could not process image for scene {scene['order_index']}")
                continue
            
            # Guardar la URL local en la base de datos
            asset_id = str(uuid.uuid4())
            
            print(f"💾 Saving asset to database...")
            print(f"   Asset ID: {asset_id}")
            print(f"   Scene ID: {scene['id']}")
            print(f"   Local URL: {final_url}")
            print(f"   File: {filename}")
            
            # Crear registro del asset
            try:
                metadata_json = json.dumps({
                    "filename": filename,
                    "scene_title": scene["title"],
                    "original_source": result.get("success", False)
                })
                await turso_client.execute(
                    """INSERT INTO assets (
                        id, scene_id, type, url, status, metadata, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    [
                        asset_id,
                        scene["id"],
                        "image",
                        final_url,
                        "completed",
                        metadata_json,
                        datetime.utcnow().isoformat()
                    ]
                )
                print(f"✅ Asset saved to database: {asset_id}")
            except Exception as db_error:
                print(f"❌ Database error: {db_error}")
                import traceback
                traceback.print_exc()
                continue
            
            # Actualizar estado de la escena
            await turso_client.execute(
                "UPDATE scenes SET status = ? WHERE id = ?",
                ["image_ready", scene["id"]]
            )
            
            generated_count += 1
            
        except Exception as e:
            print(f"Error generating image for scene {scene['id']}: {e}")
            # Continuar con la siguiente escena
            continue
    
    # Actualizar estado del proyecto
    if generated_count > 0:
        await turso_client.execute(
            "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
            ["images_ready", datetime.utcnow().isoformat(), project_id]
        )
    
    return {
        "project_id": project_id,
        "total_scenes": len(scenes_result),
        "images_generated": generated_count,
        "status": "completed" if generated_count == len(scenes_result) else "partial"
    }


@router.get("/generate-images-stream/{project_id}")
async def generate_images_stream(
    project_id: str,
    provider: str = "dalle"
):
    """
    Generar imágenes con Server-Sent Events (SSE) para progreso en tiempo real.
    El cliente recibe actualizaciones cada vez que se genera una imagen.
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        from app.services.image_service import ImageService
        from app.services.higgsfield_service import HiggsfieldService
        from app.services.dalle_service import DalleService
        from app.services.gemini_image_service import GeminiImageService
        from app.services.storage_service import StorageService
        import base64
        from pathlib import Path
        
        turso_client = get_turso_client()
        
        # Verificar que el proyecto existe
        project_result = await turso_client.execute(
            "SELECT id, title, style FROM projects WHERE id = ?",
            [project_id]
        )
        
        if not project_result or len(project_result) == 0:
            yield f"data: {json.dumps({'type': 'error', 'message': 'Project not found'})}\n\n"
            return
        
        project = project_result[0]
        
        # Obtener las escenas del proyecto
        scenes_result = await turso_client.execute(
            "SELECT id, image_prompt, title, order_index FROM scenes WHERE project_id = ? ORDER BY order_index",
            [project_id]
        )
        
        if not scenes_result or len(scenes_result) == 0:
            yield f"data: {json.dumps({'type': 'error', 'message': 'No scenes found'})}\n\n"
            return
        
        total_scenes = len(scenes_result)
        
        # Enviar evento inicial
        yield f"data: {json.dumps({'type': 'start', 'total': total_scenes, 'message': f'Iniciando generación de {total_scenes} imágenes...'})}\n\n"
        
        # Seleccionar el servicio según el proveedor
        if provider == "higgsfield":
            image_generator = HiggsfieldService()
        elif provider == "aimlapi":
            image_generator = ImageService()
        elif provider == "gemini":
            image_generator = GeminiImageService()
        else:
            image_generator = DalleService()
        
        storage = StorageService()
        generated_count = 0
        
        # Crear directorio de imágenes si no existe
        images_dir = Path("uploads/images")
        images_dir.mkdir(parents=True, exist_ok=True)
        
        for index, scene in enumerate(scenes_result):
            scene_number = index + 1
            
            # Enviar evento de progreso
            scene_title = scene['title']
            progress_msg = f"Generando imagen {scene_number}/{total_scenes}: {scene_title}"
            yield f"data: {json.dumps({'type': 'progress', 'current': scene_number, 'total': total_scenes, 'scene_title': scene_title, 'message': progress_msg})}\n\n"
            
            try:
                # Generar imagen
                result = await image_generator.generate_image(
                    prompt=scene["image_prompt"],
                    width=1024,
                    height=768,
                    style=project.get("style", "cinematic")
                )
                
                image_url = result.get("image_url") or result.get("url")
                
                if not image_url:
                    yield f"data: {json.dumps({'type': 'scene_error', 'scene': scene_number, 'message': f'No se pudo generar imagen para escena {scene_number}'})}\n\n"
                    continue
                
                # Nombre de archivo único
                filename = f"scene_{project_id[:8]}_{scene['order_index']:02d}_{scene['id'][:8]}.png"
                file_path = images_dir / filename
                
                # Procesar imagen
                final_url = None
                
                if image_url.startswith("data:"):
                    try:
                        header, encoded = image_url.split(",", 1)
                        image_bytes = base64.b64decode(encoded)
                        with open(file_path, "wb") as f:
                            f.write(image_bytes)
                        final_url = f"http://localhost:8000/api/v1/assets/image/{filename}"
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'scene_error', 'scene': scene_number, 'message': f'Error guardando imagen: {str(e)}'})}\n\n"
                        continue
                        
                elif image_url.startswith("http"):
                    try:
                        import httpx
                        async with httpx.AsyncClient(timeout=30.0) as http_client:
                            img_response = await http_client.get(image_url)
                            if img_response.status_code == 200:
                                with open(file_path, "wb") as f:
                                    f.write(img_response.content)
                                final_url = f"http://localhost:8000/api/v1/assets/image/{filename}"
                    except Exception as e:
                        yield f"data: {json.dumps({'type': 'scene_error', 'scene': scene_number, 'message': f'Error descargando imagen: {str(e)}'})}\n\n"
                        continue
                
                if not final_url:
                    continue
                
                # Guardar en base de datos
                asset_id = str(uuid.uuid4())
                metadata_json = json.dumps({"filename": filename, "scene_title": scene["title"]})
                await turso_client.execute(
                    """INSERT INTO assets (
                        id, scene_id, type, url, status, metadata, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    [
                        asset_id,
                        scene["id"],
                        "image",
                        final_url,
                        "completed",
                        metadata_json,
                        datetime.utcnow().isoformat()
                    ]
                )
                
                await turso_client.execute(
                    "UPDATE scenes SET status = ? WHERE id = ?",
                    ["image_ready", scene["id"]]
                )
                
                generated_count += 1
                
                # Enviar evento de éxito para esta escena
                yield f"data: {json.dumps({'type': 'scene_complete', 'scene': scene_number, 'total': total_scenes, 'image_url': final_url, 'message': f'✅ Imagen {scene_number}/{total_scenes} completada'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'scene_error', 'scene': scene_number, 'message': f'Error: {str(e)}'})}\n\n"
                continue
        
        # Actualizar estado del proyecto
        if generated_count > 0:
            await turso_client.execute(
                "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
                ["images_ready", datetime.utcnow().isoformat(), project_id]
            )
        
        # Enviar evento final
        yield f"data: {json.dumps({'type': 'complete', 'generated': generated_count, 'total': total_scenes, 'message': f'✅ {generated_count}/{total_scenes} imágenes generadas'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/video-providers")
async def get_video_providers():
    """
    Lista todos los proveedores de video disponibles y sus capacidades
    """
    from app.services.unified_video_service import unified_video_service
    
    return unified_video_service.list_providers()


@router.post("/animate-scene", response_model=Dict)
async def animate_scene(
    scene_id: str,
    background_tasks: BackgroundTasks,
    duration: float = 5.0,
    motion_type: str = "auto",
    provider: str = "kling"
):
    """
    Animar una escena específica usando el proveedor de video especificado.
    Genera un video corto animado a partir de la imagen de la escena.
    
    Proveedores disponibles:
    - kling: Kling AI (disponible)
    - veo: Google Veo (disponible)
    """
    from app.services.unified_video_service import unified_video_service
    from app.services.storage_service import StorageService
    
    turso_client = get_turso_client()
    
    # Obtener la escena y su imagen
    scene_result = await turso_client.execute(
        """SELECT s.id, s.project_id, s.title, s.image_url, s.order_index, p.title as project_title
           FROM scenes s
           JOIN projects p ON s.project_id = p.id
           WHERE s.id = ?""",
        [scene_id]
    )
    
    if not scene_result or len(scene_result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scene not found"
        )
    
    scene = scene_result[0]
    
    if not scene.get("image_url"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scene does not have an image. Generate images first."
        )
    
    # Actualizar estado de la escena
    await turso_client.execute(
        "UPDATE scenes SET video_status = ?, updated_at = ? WHERE id = ?",
        ["animating", datetime.utcnow().isoformat(), scene_id]
    )
    
    try:
        print(f"🎬 Starting animation for scene {scene['order_index']}: {scene['title']} (Provider: {provider})")
        
        # Iniciar animación con el proveedor elegido
        result = await unified_video_service.animate_image(
            image_url=scene["image_url"],
            duration=duration,
            motion_type=motion_type,
            provider=provider
        )
        
        # Verificar si el proveedor está disponible
        if not result.get("success", True):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=result.get("message", result.get("error", "Provider not available"))
            )
        
        task_id = result.get("task_id")
        
        if not task_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to start animation"
            )
        
        print(f"✅ Animation task started: {task_id}")
        
        # Guardar task_id en la escena
        await turso_client.execute(
            "UPDATE scenes SET video_task_id = ?, video_provider = ? WHERE id = ?",
            [task_id, provider, scene_id]
        )
        
        return {
            "scene_id": scene_id,
            "task_id": task_id,
            "provider": provider,
            "status": "processing",
            "message": "Animation started successfully"
        }
        
    except Exception as e:
        print(f"❌ Error animating scene: {e}")
        await turso_client.execute(
            "UPDATE scenes SET video_status = ?, updated_at = ? WHERE id = ?",
            ["failed", datetime.utcnow().isoformat(), scene_id]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Animation failed: {str(e)}"
        )


@router.get("/animation-status/{task_id}", response_model=Dict)
async def get_animation_status(task_id: str, provider: str = "kling"):
    """
    Obtener el estado de una animación en progreso.
    
    Args:
        task_id: ID de la tarea
        provider: Proveedor usado (kling, veo, etc.)
    """
    from app.services.unified_video_service import unified_video_service
    from app.services.storage_service import StorageService
    
    try:
        status = await unified_video_service.get_animation_status(task_id, provider)
        
        # Si el video está completo, descargarlo y subirlo a storage
        if status.get("status") == "completed" and status.get("video_url"):
            turso_client = get_turso_client()
            
            # Buscar la escena asociada
            scene_result = await turso_client.execute(
                "SELECT id, project_id FROM scenes WHERE video_task_id = ?",
                [task_id]
            )
            
            if scene_result and len(scene_result) > 0:
                scene = scene_result[0]
                video_url = status.get("video_url")
                
                # Actualizar la escena con la URL del video
                await turso_client.execute(
                    """UPDATE scenes 
                       SET video_url = ?, video_status = ?, updated_at = ? 
                       WHERE id = ?""",
                    [video_url, "completed", datetime.utcnow().isoformat(), scene["id"]]
                )
                
                print(f"✅ Video completed and saved for scene {scene['id']}")
        
        return status
        
    except Exception as e:
        print(f"❌ Error checking animation status: {e}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.post("/animate-scenes/{project_id}")
async def animate_scenes(
    project_id: str,
    background_tasks: BackgroundTasks,
    duration: float = 5.0,
    motion_type: str = "auto",
    provider: str = "veo"
):
    """
    Animar todas las escenas del proyecto.
    Genera videos cortos animados a partir de las imágenes.
    Soporta múltiples proveedores: veo (Gemini), kling (AIMLAPI)
    """
    from app.services.unified_video_service import unified_video_service
    
    turso_client = get_turso_client()
    
    print(f"🎬 Starting scene animation with provider: {provider}")
    
    # Verificar que el proyecto existe
    project_result = await turso_client.execute(
        "SELECT id, title FROM projects WHERE id = ?",
        [project_id]
    )
    
    if not project_result or len(project_result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Obtener escenas con sus imágenes desde la tabla assets
    scenes_result = await turso_client.execute(
        """SELECT DISTINCT s.id, s.title, s.order_index, a.url as image_url
           FROM scenes s
           INNER JOIN assets a ON s.id = a.scene_id
           WHERE s.project_id = ? AND a.type = 'image' AND a.status = 'completed'
           ORDER BY s.order_index""",
        [project_id]
    )
    
    if not scenes_result or len(scenes_result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No scenes with images found. Generate images first."
        )
    
    # Actualizar estado del proyecto
    await turso_client.execute(
        "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
        ["animating", datetime.utcnow().isoformat(), project_id]
    )
    
    animated_count = 0
    failed_count = 0
    tasks = []
    
    for scene in scenes_result:
        try:
            print(f"🎨 Animating scene {scene['order_index']}: {scene['title']}")
            
            # Actualizar estado de la escena
            await turso_client.execute(
                "UPDATE scenes SET status = ?, updated_at = ? WHERE id = ?",
                ["animating", datetime.utcnow().isoformat(), scene["id"]]
            )
            
            # Iniciar animación con el proveedor seleccionado
            result = await unified_video_service.animate_image(
                image_url=scene["image_url"],
                duration=duration,
                motion_type=motion_type,
                provider=provider
            )
            
            if not result.get("success", True):
                print(f"❌ Animation failed for scene {scene['order_index']}: {result.get('error')}")
                failed_count += 1
                await turso_client.execute(
                    "UPDATE scenes SET status = ? WHERE id = ?",
                    ["image_ready", scene["id"]]
                )
                continue
            
            task_id = result.get("task_id")
            
            if task_id:
                # Guardar task_id y provider
                await turso_client.execute(
                    "UPDATE scenes SET video_task_id = ?, video_provider = ? WHERE id = ?",
                    [task_id, provider, scene["id"]]
                )
                tasks.append({
                    "scene_id": scene["id"],
                    "scene_title": scene["title"],
                    "task_id": task_id,
                    "provider": provider
                })
                animated_count += 1
                print(f"✅ Animation started for scene {scene['order_index']}: {task_id}")
            else:
                failed_count += 1
                await turso_client.execute(
                    "UPDATE scenes SET status = ? WHERE id = ?",
                    ["image_ready", scene["id"]]
                )
                
        except Exception as e:
            print(f"❌ Failed to animate scene {scene['order_index']}: {e}")
            import traceback
            traceback.print_exc()
            failed_count += 1
            await turso_client.execute(
                "UPDATE scenes SET status = ? WHERE id = ?",
                ["image_ready", scene["id"]]
            )
    
    # Si todas fallaron, revertir estado del proyecto
    if animated_count == 0:
        await turso_client.execute(
            "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
            ["images_ready", datetime.utcnow().isoformat(), project_id]
        )
    
    return {
        "project_id": project_id,
        "total_scenes": len(scenes_result),
        "animated": animated_count,
        "failed": failed_count,
        "tasks": tasks,
        "provider": provider,
        "message": f"Started animation for {animated_count}/{len(scenes_result)} scenes using {provider}"
    }


@router.post("/prepare-for-editor/{project_id}")
async def prepare_for_editor(project_id: str):
    """
    Organiza todos los clips animados en Google Drive
    para que el editor pueda ensamblar el video final
    """
    from app.services.storage_service import StorageService
    
    turso_client = get_turso_client()
    
    # Verificar proyecto
    project_result = await turso_client.execute(
        "SELECT id, title FROM projects WHERE id = ?",
        [project_id]
    )
    
    if not project_result or len(project_result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = project_result[0]
    
    # Obtener todas las escenas con videos
    scenes_result = await turso_client.execute(
        """SELECT id, title, order_index, video_url, duration, dialogue
           FROM scenes 
           WHERE project_id = ? AND video_url IS NOT NULL
           ORDER BY order_index""",
        [project_id]
    )
    
    if not scenes_result or len(scenes_result) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No animated scenes found. Animate scenes first."
        )
    
    storage = StorageService()
    
    # Crear carpeta en Drive
    folder_name = f"{project['title']} - Clips"
    
    # Crear manifest para el editor
    manifest = {
        "project_id": project_id,
        "project_title": project["title"],
        "total_scenes": len(scenes_result),
        "scenes": []
    }
    
    for scene in scenes_result:
        manifest["scenes"].append({
            "order": scene["order_index"],
            "title": scene["title"],
            "video_url": scene["video_url"],
            "duration": scene["duration"],
            "dialogue": scene["dialogue"]
        })
    
    # Actualizar estado del proyecto
    await turso_client.execute(
        "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
        ["ready_for_edit", datetime.utcnow().isoformat(), project_id]
    )
    
    return {
        "project_id": project_id,
        "status": "ready",
        "total_clips": len(scenes_result),
        "manifest": manifest,
        "message": "Project ready for editing"
    }
