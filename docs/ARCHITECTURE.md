# Arquitectura del Sistema

## Flujo de Trabajo

```
1. Usuario ingresa guión/idea
   ↓
2. LLM analiza y genera escenas (OpenAI/Anthropic)
   - Divide en escenas visuales
   - Genera descripciones detalladas
   - Crea prompts optimizados
   ↓
3. Higgsfield genera imágenes
   - Una imagen por escena
   - Basado en prompts optimizados
   - Se suben a Google Drive
   ↓
4. Kling anima las imágenes
   - Convierte cada imagen en video corto (5-10s)
   - Agrega movimiento cinematográfico
   - Se suben a Google Drive
   ↓
5. Editor manual ensambla el trailer
   - Todos los clips organizados en Drive
   - El editor usa su herramienta preferida
   - Agrega transiciones, música, efectos finales
   - (Posible automatización futura)
```

## Componentes Principales

### Backend (FastAPI)

- **API REST**: Endpoints para CRUD de proyectos, escenas y assets
- **Database**: Turso (LibSQL) - SQLite serverless
- **Cache**: Redis para caching y colas
- **Tasks**: Celery para procesamiento asíncrono

### Servicios

1. **LLM Service**
   - Integración con OpenAI/Anthropic
   - Análisis y división de guiones
   - Generación de prompts para imágenes

2. **Higgsfield Service**
   - Generación de imágenes estáticas
   - Gestión de requests y polling
   - Descarga de assets

3. **Kling Service**
   - Animación de imágenes a video
   - Videos cortos de 5-10 segundos
   - Movimientos cinematográficos

4. **Storage Service**
   - Google Drive API
   - Organización de archivos por proyecto
   - Links de visualización compartibles

### Frontend (Next.js)

- **Dashboard**: Vista de proyectos
- **Editor**: Creación y edición de guiones
- **Storyboard**: Vista de escenas generadas
- **Gallery**: Vista de imágenes y clips en Drive
- **Export**: Información para el editor

## Base de Datos (Turso)

### Ventajas de Turso
- SQLite serverless ultra-rápido
- Edge-hosted (baja latencia)
- Sincronización automática
- Gratis para empezar
- Compatible con SQLAlchemy

### Tablas

1. **projects**
   - Proyecto principal
   - Guión original
   - Estado del proceso
   - Google Drive folder ID

2. **scenes**
   - Escenas individuales
   - Descripciones y prompts
   - Referencias a assets

3. **assets**
   - Archivos multimedia
   - Google Drive file IDs
   - Links de visualización
   - Info de generación

## Storage (Google Drive)

### Estructura de Carpetas

```
HeyAI Projects/
├── Project-1234/
│   ├── images/
│   │   ├── scene-01.jpg
│   │   ├── scene-02.jpg
│   │   └── ...
│   ├── clips/
│   │   ├── scene-01-animated.mp4
│   │   ├── scene-02-animated.mp4
│   │   └── ...
│   └── final/
│       └── trailer-final.mp4 (editado por humano)
```

### Ventajas
- ✅ Visualización fácil de assets
- ✅ Compartir links con el equipo
- ✅ Colaboración en tiempo real
- ✅ Preview automático de imágenes/videos
- ✅ No hay límite de almacenamiento (con workspace)

## Procesamiento Asíncrono

### Celery Tasks

1. **analyze_script_task**: Analizar guión con LLM
2. **generate_scene_image**: Generar imagen individual
3. **generate_all_images**: Generar todas las imágenes
4. **animate_scene_image**: Animar imagen con Kling
5. **animate_all_scenes**: Animar todas las escenas
6. **upload_clips_to_drive**: Organizar clips para editor

## Estados del Proyecto

- `draft`: Borrador inicial
- `processing_script`: Analizando guión con LLM
- `generating_images`: Generando imágenes con Higgsfield
- `animating_scenes`: Animando imágenes con Kling
- `ready_for_edit`: Clips listos para editor
- `completed`: Video final editado
- `failed`: Error en el proceso

## Workflow del Editor

1. Sistema genera todas las escenas animadas
2. Se organizan en carpeta de Google Drive
3. Se envía link al editor con:
   - Todos los clips numerados
   - Guión con timing sugerido
   - Referencias visuales
4. Editor usa DaVinci/Premiere/Final Cut
5. Agrega transiciones, música, color grading
6. Sube video final a carpeta `final/`

## Próximos Pasos

1. ✅ Implementar integración completa con LLM
2. ✅ Implementar integración con Higgsfield
3. ✅ Implementar integración con Kling
4. ✅ Configurar Google Drive API
5. 🔄 Crear interfaz de usuario completa
6. 🔄 Sistema de preview de clips en Drive
7. 🔄 Workflow de aprobación de escenas
8. 🔄 Posible automatización de ensamblaje futuro
