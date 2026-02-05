# Guía de Kling AI Setup

## ¿Qué es Kling AI?

Kling es una plataforma de IA china para animación de imágenes a video de alta calidad:
- 🎬 Convierte imágenes estáticas en videos cinematográficos
- ⚡ Videos de hasta 10 segundos
- 🎨 Control de movimiento (zoom, pan, camera motion)
- 🎭 Calidad cinematográfica

## Alternativas Similares

Si Kling no está disponible, puedes usar:
- **Runway Gen-2**: Similar, muy usado en industria
- **Pika Labs**: Otra opción popular
- **Stability AI**: Video generación
- **LeiaPix**: Específico para depth/motion

## Paso 1: Obtener API Key

> ⚠️ **Nota**: Al momento de escribir esto (Feb 2026), Kling puede requerir acceso beta o no tener API pública. Verifica su sitio oficial.

### Opciones:

1. **API Oficial** (si está disponible):
   - Ve a [Kling AI Website](https://klingai.com)
   - Crea cuenta
   - Ve a Developer/API section
   - Genera API key

2. **Usando Runway como alternativa**:
   ```env
   KLING_API_KEY=tu-runway-api-key
   KLING_API_URL=https://api.runwayml.com/v1
   ```

## Paso 2: Configurar Variables de Entorno

En `backend/.env`:

```env
# Kling AI
KLING_API_KEY=tu-api-key-aqui
KLING_API_URL=https://api.klingai.com/v1
```

## Paso 3: Estructura de la API (Ejemplo)

El servicio está preparado para:

```python
# Animar una imagen
result = await kling_service.animate_image(
    image_url="https://drive.google.com/.../scene-01.jpg",
    duration=5.0,
    motion_type="cinematic"
)

# Esperar resultado
video = await kling_service.wait_for_animation(
    task_id=result["task_id"]
)

# Descargar video
video_bytes = await kling_service.download_video(
    video_url=video["video_url"]
)
```

## Tipos de Movimiento Disponibles

```python
motion_types = [
    "auto",        # Kling decide el mejor movimiento
    "zoom_in",     # Zoom hacia adelante
    "zoom_out",    # Zoom hacia atrás
    "pan_left",    # Paneo a la izquierda
    "pan_right",   # Paneo a la derecha
    "tilt_up",     # Inclinación hacia arriba
    "tilt_down",   # Inclinación hacia abajo
    "orbit",       # Movimiento orbital
    "crane",       # Movimiento de grúa
]
```

## Parámetros Comunes

```python
{
    "image_url": "url-de-la-imagen",
    "duration": 5.0,              # 1-10 segundos
    "motion_type": "auto",
    "motion_strength": 0.5,       # 0.0-1.0
    "fps": 24,                    # 24 o 30
    "resolution": "1080p",        # 720p, 1080p, 4k
    "aspect_ratio": "16:9",       # 16:9, 9:16, 1:1
}
```

## Ejemplo de Uso en el Proyecto

```python
# En generation_tasks.py
from app.services.kling_service import kling_service
from app.services.storage_service import storage_service

async def animate_scene(scene_id: str):
    # Obtener escena de BD
    scene = await get_scene(scene_id)
    
    # Obtener URL de imagen desde Google Drive
    image_url = scene.image_asset.file_path
    
    # Animar con Kling
    result = await kling_service.animate_image(
        image_url=image_url,
        duration=scene.duration or 5.0,
        motion_type="cinematic"
    )
    
    # Esperar a que termine
    video = await kling_service.wait_for_animation(
        task_id=result["task_id"]
    )
    
    # Descargar video
    video_bytes = await kling_service.download_video(
        video["video_url"]
    )
    
    # Subir a Google Drive
    drive_info = await storage_service.save_file(
        file_content=video_bytes,
        filename=f"scene-{scene.order:02d}-animated.mp4",
        folder="videos",
        mime_type="video/mp4"
    )
    
    # Actualizar scene con video asset
    await update_scene_video(scene_id, drive_info)
```

## Costos Estimados

Los costos varían según el proveedor:

### Kling AI (estimado)
- ~$0.10 - $0.50 por video de 5s
- Paquetes mensuales disponibles

### Runway Gen-2 (alternativa)
- $0.05 por segundo de video
- Video de 5s = $0.25
- Plan pro: $35/mes con 625 segundos incluidos

### Pika Labs (alternativa)
- Plan básico: $10/mes
- Plan estándar: $35/mes
- Plan unlimited: $95/mes

## Tips para Mejores Resultados

1. **Calidad de Imagen**:
   - Usar imágenes de alta resolución
   - Mínimo 1024x768
   - Mejor: 1920x1080 o superior

2. **Composición**:
   - Imágenes con profundidad funcionan mejor
   - Evitar imágenes muy planas
   - Sujetos bien definidos

3. **Motion Type**:
   - "auto" suele dar buenos resultados
   - Para control específico, elegir manualmente
   - Probar diferentes opciones

4. **Duración**:
   - 5 segundos es óptimo
   - Videos muy cortos (<3s) pueden sentirse abruptos
   - Videos muy largos (>7s) pueden perder calidad

## Fallback Local (Sin API)

Si no tienes acceso a Kling, puedes implementar animación básica:

```python
# Usando Ken Burns effect con OpenCV/MoviePy
import cv2
import numpy as np

def create_ken_burns_video(image_path, duration=5):
    """Efecto Ken Burns básico (zoom + pan)"""
    # Implementación simple con OpenCV
    pass
```

## Testing

```bash
# Test básico de la integración
cd backend
python -c "
import asyncio
from app.services.kling_service import kling_service

async def test():
    try:
        # Intenta hacer ping a la API
        result = await kling_service.animate_image(
            image_url='test',
            duration=5.0
        )
        print('✅ Kling API respondiendo')
    except Exception as e:
        print(f'⚠️  Error: {e}')

asyncio.run(test())
"
```

## Recursos

- [Kling AI Official](https://klingai.com)
- [Runway Gen-2](https://runwayml.com)
- [Pika Labs](https://pika.art)
