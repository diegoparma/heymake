# Kling AI Video Generation Setup

Kling AI es una plataforma de generación de videos con IA que permite animar imágenes estáticas.

## 1. Obtener API Key de Kling

1. Visita [Kling AI](https://klingai.com)
2. Crea una cuenta o inicia sesión
3. Ve a tu perfil → API Settings
4. Genera una nueva API key
5. Copia el API key y guárdalo de forma segura

## 2. Configuración en .env

Agrega las siguientes variables a tu archivo `.env`:

```bash
# Kling AI Configuration
KLING_API_KEY=your_kling_api_key_here
KLING_API_URL=https://api.klingai.com/v1
```

## 3. Endpoints Disponibles

### Animar una Escena Individual

```bash
POST /api/v1/generation/animate-scene
```

**Parámetros:**
- `scene_id`: ID de la escena a animar
- `duration`: Duración del video (1-10 segundos, default: 5)
- `motion_type`: Tipo de movimiento (auto, zoom_in, zoom_out, pan_left, pan_right)

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/api/v1/generation/animate-scene?scene_id=abc123&duration=5&motion_type=auto"
```

### Verificar Estado de Animación

```bash
GET /api/v1/generation/animation-status/{task_id}
```

**Ejemplo:**
```bash
curl "http://localhost:8000/api/v1/generation/animation-status/task_xyz"
```

### Animar Todas las Escenas del Proyecto

```bash
POST /api/v1/generation/animate-scenes/{project_id}
```

**Parámetros:**
- `project_id`: ID del proyecto
- `duration`: Duración de cada video (default: 5)
- `motion_type`: Tipo de movimiento para todos los videos

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/api/v1/generation/animate-scenes/project123?duration=5&motion_type=auto"
```

### Preparar para Edición

```bash
POST /api/v1/generation/prepare-for-editor/{project_id}
```

Organiza todos los clips animados y genera un manifest para el editor.

## 4. Flujo de Trabajo Completo

1. **Crear Proyecto**
   ```bash
   POST /api/v1/projects
   ```

2. **Analizar Guión**
   ```bash
   POST /api/v1/generation/analyze-script
   ```

3. **Generar Imágenes**
   ```bash
   POST /api/v1/generation/generate-images/{project_id}
   ```

4. **Animar Escenas**
   ```bash
   POST /api/v1/generation/animate-scenes/{project_id}
   ```

5. **Monitorear Progreso**
   ```bash
   GET /api/v1/generation/animation-status/{task_id}
   ```

6. **Preparar para Editor**
   ```bash
   POST /api/v1/generation/prepare-for-editor/{project_id}
   ```

## 5. Tipos de Movimiento

- **auto**: Kling decide automáticamente el mejor movimiento
- **zoom_in**: Acercamiento a la imagen
- **zoom_out**: Alejamiento de la imagen
- **pan_left**: Paneo hacia la izquierda
- **pan_right**: Paneo hacia la derecha

## 6. Límites y Consideraciones

- Duración máxima: 10 segundos por video
- Duración mínima: 1 segundo
- El procesamiento puede tomar varios minutos por video
- Los videos se guardan automáticamente en la base de datos

## 7. Estados de Video

En la tabla `scenes`, los videos pueden tener los siguientes estados:

- **pending**: No se ha iniciado la animación
- **animating**: La animación está en proceso
- **completed**: Video generado exitosamente
- **failed**: Error en la generación

## 8. Resolución de Problemas

### Error: "Scene does not have an image"
Genera las imágenes primero usando el endpoint `/generate-images/`.

### Error: "Failed to start animation"
Verifica que tu API key de Kling sea válida y que tengas créditos suficientes.

### Video tarda mucho en procesarse
Kling puede tomar de 2-5 minutos por video dependiendo de la complejidad y la carga del servidor.
