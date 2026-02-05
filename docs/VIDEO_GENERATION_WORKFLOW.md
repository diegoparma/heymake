# Flujo Completo de Generación de Video

Este documento describe el flujo completo desde un guión hasta los clips de video listos para editar.

## 🚀 Pipeline Completo

```
Guión → Análisis LLM → Escenas → Imágenes → Videos → Edición
```

## 📋 Paso a Paso

### 1. Crear Proyecto

```bash
POST http://localhost:8000/api/v1/projects

{
  "title": "Mi Trailer Épico",
  "description": "Un trailer cinematográfico",
  "style": "cinematic",
  "duration_target": 60
}
```

**Respuesta:**
```json
{
  "id": "project-123",
  "title": "Mi Trailer Épico",
  "status": "draft"
}
```

### 2. Analizar Guión (Generar Escenas con LLM)

```bash
POST http://localhost:8000/api/v1/generation/analyze-script

{
  "project_id": "project-123",
  "script": "Un héroe solitario camina por un páramo desolado. El viento sopla con fuerza. De repente, ve una luz en el horizonte...",
  "style": "cinematic",
  "num_scenes": 5,
  "duration_target": 60
}
```

**Respuesta:**
```json
{
  "project_id": "project-123",
  "scenes": [
    {
      "order": 1,
      "title": "Héroe en el páramo",
      "description": "Plano amplio de un héroe caminando solo...",
      "dialogue": null,
      "image_prompt": "A lone hero walking through a desolate wasteland, cinematic lighting...",
      "duration": 5.0
    },
    {
      "order": 2,
      "title": "El viento",
      "description": "Close-up del rostro del héroe...",
      "dialogue": null,
      "image_prompt": "Close-up of a hero's face in strong wind, dramatic...",
      "duration": 4.0
    }
    // ... más escenas
  ],
  "total_scenes": 5,
  "estimated_duration": 30.0
}
```

### 3. Generar Imágenes para las Escenas

```bash
POST http://localhost:8000/api/v1/generation/generate-images/project-123?provider=dalle

# Providers disponibles:
# - dalle (OpenAI DALL-E) - Default
# - aimlapi (Flux via AIMLAPI)
# - higgsfield (Higgsfield AI)
# - gemini (Google Gemini)
```

**Respuesta:**
```json
{
  "project_id": "project-123",
  "total_scenes": 5,
  "images_generated": 5,
  "status": "completed"
}
```

Este paso puede tomar varios minutos dependiendo del número de escenas y el proveedor.

### 4. Animar Escenas (Generar Videos)

#### Opción A: Animar una escena específica

```bash
POST http://localhost:8000/api/v1/generation/animate-scene?scene_id=scene-456&duration=5&motion_type=auto
```

**Respuesta:**
```json
{
  "scene_id": "scene-456",
  "task_id": "kling-task-789",
  "status": "processing",
  "message": "Animation started successfully"
}
```

#### Opción B: Animar todas las escenas del proyecto

```bash
POST http://localhost:8000/api/v1/generation/animate-scenes/project-123?duration=5&motion_type=auto
```

**Respuesta:**
```json
{
  "project_id": "project-123",
  "total_scenes": 5,
  "animated": 5,
  "failed": 0,
  "tasks": [
    {"scene_id": "scene-1", "task_id": "task-1"},
    {"scene_id": "scene-2", "task_id": "task-2"}
    // ...
  ],
  "message": "Started animation for 5 scenes"
}
```

### 5. Monitorear Progreso de Animación

```bash
GET http://localhost:8000/api/v1/generation/animation-status/kling-task-789
```

**Respuesta (en proceso):**
```json
{
  "task_id": "kling-task-789",
  "status": "processing",
  "progress": 65,
  "video_url": null
}
```

**Respuesta (completado):**
```json
{
  "task_id": "kling-task-789",
  "status": "completed",
  "progress": 100,
  "video_url": "https://kling-cdn.com/videos/video-789.mp4"
}
```

### 6. Obtener Estado del Proyecto

```bash
GET http://localhost:8000/api/v1/projects/project-123
```

**Respuesta:**
```json
{
  "id": "project-123",
  "title": "Mi Trailer Épico",
  "status": "animating",
  "scenes": [
    {
      "id": "scene-1",
      "order_index": 1,
      "title": "Héroe en el páramo",
      "image_url": "http://localhost:8000/api/v1/assets/image/scene_project-123_01.png",
      "video_url": "https://kling-cdn.com/videos/video-789.mp4",
      "video_status": "completed",
      "duration": 5.0
    }
    // ... más escenas
  ]
}
```

### 7. Preparar para Edición

Una vez que todos los videos estén completos:

```bash
POST http://localhost:8000/api/v1/generation/prepare-for-editor/project-123
```

**Respuesta:**
```json
{
  "project_id": "project-123",
  "status": "ready",
  "total_clips": 5,
  "manifest": {
    "project_id": "project-123",
    "project_title": "Mi Trailer Épico",
    "total_scenes": 5,
    "scenes": [
      {
        "order": 1,
        "title": "Héroe en el páramo",
        "video_url": "https://...",
        "duration": 5.0,
        "dialogue": null
      }
      // ... más escenas
    ]
  },
  "message": "Project ready for editing"
}
```

## ⏱️ Tiempos Estimados

| Paso | Tiempo Estimado |
|------|----------------|
| Crear Proyecto | < 1 segundo |
| Analizar Guión (5 escenas) | 10-30 segundos |
| Generar Imágenes (5 escenas) | 2-5 minutos |
| Animar Videos (5 escenas) | 10-25 minutos |
| **Total** | **~15-30 minutos** |

## 🎨 Tipos de Movimiento para Videos

- `auto`: Kling decide el mejor movimiento
- `zoom_in`: Acercamiento
- `zoom_out`: Alejamiento
- `pan_left`: Paneo izquierda
- `pan_right`: Paneo derecha

## 📊 Estados del Sistema

### Estados del Proyecto
- `draft`: Recién creado
- `analyzing`: Analizando guión
- `scenes_ready`: Escenas generadas
- `generating_images`: Generando imágenes
- `images_ready`: Imágenes listas
- `animating`: Generando videos
- `ready_for_edit`: Listo para edición
- `completed`: Proyecto completo

### Estados de Video (Escena)
- `pending`: No iniciado
- `animating`: En proceso
- `completed`: Completado
- `failed`: Error

## 🔧 Script de Ejemplo Completo

```bash
#!/bin/bash
API_URL="http://localhost:8000/api/v1"

# 1. Crear proyecto
PROJECT_ID=$(curl -s -X POST "$API_URL/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mi Trailer",
    "style": "cinematic"
  }' | jq -r '.id')

echo "Proyecto creado: $PROJECT_ID"

# 2. Analizar guión
curl -s -X POST "$API_URL/generation/analyze-script" \
  -H "Content-Type: application/json" \
  -d "{
    \"project_id\": \"$PROJECT_ID\",
    \"script\": \"Un héroe camina por el desierto...\"
  }"

# 3. Generar imágenes
curl -s -X POST "$API_URL/generation/generate-images/$PROJECT_ID?provider=dalle"

# 4. Animar escenas
curl -s -X POST "$API_URL/generation/animate-scenes/$PROJECT_ID?duration=5&motion_type=auto"

# 5. Monitorear hasta completar
# (implementar polling aquí)

# 6. Preparar para editor
curl -s -X POST "$API_URL/generation/prepare-for-editor/$PROJECT_ID"
```

## 🐛 Troubleshooting

### Error: "Scene does not have an image"
**Solución:** Ejecuta `generate-images` primero.

### Error: "No scenes with images found"
**Solución:** Verifica que las imágenes se generaron correctamente.

### Video tarda mucho
**Causa:** Kling puede tomar 2-5 minutos por video. Es normal.
**Solución:** Usa el endpoint `animation-status` para monitorear.

### Error: "Failed to start animation"
**Causas posibles:**
- API key de Kling inválida
- Sin créditos en Kling
- URL de imagen inaccesible

## 📝 Notas

- Los videos generados se guardan automáticamente en la base de datos
- Puedes usar diferentes proveedores de imágenes según tu preferencia
- Los videos tienen una duración máxima de 10 segundos
- El proyecto soporta proveedores múltiples (OpenAI, Anthropic, Google) para el LLM
