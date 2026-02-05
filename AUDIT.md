# 🔍 Auditoría Completa del Código - HeyMake

**Fecha:** 5 de febrero de 2026  
**Proyecto:** HeyMake - Plataforma de generación de trailers con IA  
**Stack:** FastAPI (Python 3.12) + Next.js 14 + Turso (LibSQL) + Redis

---

## 1. 🔴 SEGURIDAD (Crítico)

### 1.1 API Keys expuestas en repositorio
- **Archivo:** `backend/.env`
- **Severidad:** 🔴 Crítica
- **Detalle:** Las API keys de Google, OpenAI, Higgsfield y tokens de Turso están en el archivo `.env` sin un `.gitignore` robusto que las proteja.
- **Riesgo:** Cualquiera con acceso al repo puede usar las credenciales.
- **Acción:** Crear `.gitignore` completo, rotar todas las keys comprometidas, usar un gestor de secretos (ej: AWS Secrets Manager, Doppler, o al menos variables de entorno del sistema).

### 1.2 Sin autenticación en endpoints
- **Archivos:** Todos los endpoints en `backend/app/api/v1/endpoints/`
- **Severidad:** 🔴 Crítica
- **Detalle:** Ningún endpoint requiere autenticación. Cualquier persona puede crear proyectos, generar imágenes, consumir créditos de las APIs.
- **Riesgo:** Uso no autorizado, consumo de créditos, acceso a datos de otros usuarios.
- **Acción:** Implementar JWT con refresh tokens, middleware de autenticación, modelo de usuarios.

### 1.3 Sin rate limiting
- **Archivo:** `backend/main.py`
- **Severidad:** 🟡 Alta
- **Detalle:** No hay límites de requests por IP o usuario. Los endpoints de generación (imágenes, videos) consumen APIs de pago.
- **Riesgo:** Un atacante puede agotar la cuota de APIs externas en minutos.
- **Acción:** Implementar `slowapi` o similar para rate limiting por IP y por usuario.

### 1.4 Sin validación de tamaño/tipo de archivos
- **Archivos:** Endpoints de upload
- **Severidad:** 🟡 Alta
- **Detalle:** No se valida el tamaño ni el tipo MIME de los archivos subidos.
- **Riesgo:** Upload de archivos maliciosos, DoS por archivos grandes.
- **Acción:** Validar tipo MIME, limitar tamaño (ej: 10MB para imágenes), sanitizar nombres de archivo.

### 1.5 CORS abierto en desarrollo
- **Archivo:** `backend/main.py`
- **Severidad:** 🟡 Media
- **Detalle:** CORS configurado con `allow_origins=["*"]` permitiendo requests desde cualquier dominio.
- **Riesgo:** En producción, cualquier sitio web podría hacer requests al API.
- **Acción:** Restringir orígenes permitidos en producción.

### 1.6 Sin HTTPS
- **Severidad:** 🟡 Media
- **Detalle:** El servidor corre en HTTP plano.
- **Riesgo:** Datos (incluyendo API keys en headers) viajan sin encriptar.
- **Acción:** Configurar TLS/SSL, idealmente detrás de un reverse proxy (nginx, Caddy).

---

## 2. 🟡 ARQUITECTURA Y MANTENIMIENTO

### 2.1 Archivo generation.py monolítico
- **Archivo:** `backend/app/api/v1/endpoints/generation.py`
- **Severidad:** 🟡 Alta
- **Detalle:** Tiene 650+ líneas. Mezcla lógica de negocio, queries SQL, manejo de errores y transformación de datos en un solo archivo.
- **Acción:** Separar en módulos:
  - `endpoints/script_analysis.py` - Análisis de guiones
  - `endpoints/image_generation.py` - Generación de imágenes
  - `endpoints/video_generation.py` - Generación de videos
  - `repositories/scene_repository.py` - Queries SQL de escenas
  - `repositories/project_repository.py` - Queries SQL de proyectos

### 2.2 Sin separación de capas (Repository Pattern)
- **Archivos:** Todos los endpoints
- **Severidad:** 🟡 Alta
- **Detalle:** Los controllers ejecutan queries SQL directamente con `turso_client.execute()`. No hay capa de repositorio ni de dominio.
- **Riesgo:** Queries duplicadas, difícil de testear, acoplamiento fuerte.
- **Acción:** Implementar Repository Pattern:
  ```
  Endpoint → Service → Repository → Database
  ```

### 2.3 Código duplicado
- **Severidad:** 🟡 Alta
- **Detalle:** La verificación de existencia de proyecto se repite en casi todos los endpoints con el mismo bloque de código (SELECT + if not result + raise HTTPException).
- **Acción:** Crear helper `get_project_or_404(project_id)` reutilizable.

### 2.4 Sin manejo centralizado de errores
- **Severidad:** 🟡 Media
- **Detalle:** Try/except dispersos por todo el código con mensajes inconsistentes.
- **Acción:** Implementar exception handlers globales en FastAPI con clases de excepción personalizadas.

### 2.5 Sin dependency injection apropiada
- **Severidad:** 🟡 Media
- **Detalle:** Los servicios se instancian inline dentro de los endpoints (ej: `ImageService()`, `LLMService()`).
- **Acción:** Usar `Depends()` de FastAPI para inyectar servicios.

### 2.6 Frontend con componentes monolíticos
- **Severidad:** 🟡 Media
- **Detalle:** Las páginas del frontend tienen componentes grandes sin separar en componentes reutilizables.
- **Acción:** Extraer componentes: `SceneCard`, `ProjectForm`, `GenerationProgress`, etc.

---

## 3. 🟡 DOCUMENTACIÓN

### 3.1 Sin README.md completo
- **Severidad:** 🟡 Alta
- **Detalle:** No hay documentación de instalación, configuración, ni uso del proyecto.
- **Acción:** Crear README.md con:
  - Descripción del proyecto
  - Requisitos del sistema
  - Instrucciones de instalación
  - Variables de entorno necesarias (sin valores)
  - Cómo ejecutar en desarrollo
  - Arquitectura del sistema

### 3.2 Sin docstrings completos en servicios
- **Severidad:** 🟡 Media
- **Detalle:** Algunas funciones tienen docstrings básicos, otras no tienen ninguno.
- **Acción:** Agregar docstrings con formato Google o NumPy a todas las funciones públicas.

### 3.3 Sin documentación de API
- **Severidad:** 🟡 Media
- **Detalle:** Solo se depende de la documentación auto-generada por FastAPI en `/docs`. No hay ejemplos de uso ni documentación de flujos.
- **Acción:** Agregar descriptions detalladas a los endpoints, ejemplos de request/response, documentar flujos de uso.

### 3.4 Sin CHANGELOG
- **Severidad:** 🟢 Baja
- **Detalle:** No hay registro de cambios ni versionado del proyecto.
- **Acción:** Crear CHANGELOG.md siguiendo el formato Keep a Changelog.

---

## 4. 🟡 CALIDAD DE CÓDIGO

### 4.1 Sin tests
- **Severidad:** 🟡 Alta
- **Detalle:** No existe ningún test unitario ni de integración. Cobertura: 0%.
- **Riesgo:** Los cambios pueden romper funcionalidad existente sin que nadie lo note.
- **Acción:**
  - Configurar pytest + pytest-asyncio
  - Tests unitarios para servicios (LLM, Image, Video)
  - Tests de integración para endpoints
  - Objetivo: 70%+ de cobertura

### 4.2 Sin linting ni formatting configurado
- **Severidad:** 🟡 Media
- **Detalle:** No hay configuración de ruff, black, isort (Python) ni eslint, prettier (JS/TS).
- **Acción:** Configurar ruff + black para Python, eslint + prettier para frontend, pre-commit hooks.

### 4.3 Type hints incompletos
- **Severidad:** 🟡 Media
- **Detalle:** El backend tiene tipado parcial. Algunas funciones retornan `Dict` genérico en lugar de modelos tipados.
- **Acción:** Completar type hints, usar `TypedDict` o Pydantic models para retornos.

### 4.4 Logging inconsistente
- **Severidad:** 🟡 Media
- **Detalle:** Se usa `print()` en lugar de `logging` en muchos servicios. Los mensajes mezclan español e inglés.
- **Acción:** Migrar a `logging` con niveles apropiados (DEBUG, INFO, WARNING, ERROR), definir idioma consistente.

### 4.5 URLs y valores hardcodeados
- **Severidad:** 🟡 Media
- **Detalle:** Hay URLs de APIs hardcodeadas en servicios en lugar de usar variables de entorno.
- **Acción:** Mover todas las URLs a configuración (settings/env).

---

## 5. 🟡 RENDIMIENTO Y ESCALABILIDAD

### 5.1 Sin caché
- **Severidad:** 🟡 Media
- **Detalle:** Redis está configurado pero no se usa para caché. Cada request consulta Turso directamente.
- **Acción:** Cachear consultas frecuentes (lista de proyectos, escenas de un proyecto) con TTL apropiado.

### 5.2 Generación secuencial de imágenes
- **Severidad:** 🟡 Media
- **Detalle:** Las imágenes de un proyecto se generan una por una en un loop secuencial.
- **Acción:** Usar `asyncio.gather()` con límite de concurrencia para paralelizar (ej: 3 imágenes simultáneas).

### 5.3 Sin cola de trabajos real
- **Severidad:** 🟡 Media
- **Detalle:** Celery está configurado en el `.env` pero no se usa. La generación de video usa polling.
- **Acción:** Implementar Celery workers para tareas de generación pesadas, con status tracking via Redis.

### 5.4 Sin compresión de imágenes
- **Severidad:** 🟢 Baja
- **Detalle:** Las imágenes generadas se guardan sin optimizar, ocupando más espacio del necesario.
- **Acción:** Comprimir con Pillow antes de guardar, generar thumbnails para la UI.

---

## 6. 🟢 INFRAESTRUCTURA

### 6.1 Sin containerización
- **Severidad:** 🟡 Media
- **Detalle:** No hay Dockerfile ni docker-compose. La configuración del entorno es manual.
- **Acción:** Crear Dockerfile para backend y frontend, docker-compose para desarrollo local.

### 6.2 Sin CI/CD
- **Severidad:** 🟡 Media
- **Detalle:** No hay pipeline de integración/deployment continuo.
- **Acción:** Configurar GitHub Actions con: lint → test → build → deploy.

### 6.3 Sin monitoreo
- **Severidad:** 🟡 Media
- **Detalle:** El health check solo verifica conexión a DB y Redis. No hay métricas ni alertas.
- **Acción:** Agregar métricas (Prometheus), logging centralizado, alertas para errores de APIs externas.

### 6.4 Sin backups automatizados
- **Severidad:** 🟡 Media
- **Detalle:** La base de datos Turso no tiene backups configurados. Los archivos generados no tienen respaldo.
- **Acción:** Configurar backups periódicos de Turso, almacenar assets en S3/GCS con redundancia.

---

## 📋 Plan de Acción Priorizado

### Fase 1: Seguridad (Urgente - Semana 1)
1. ✅ Crear `.gitignore` robusto
2. ✅ Rotar todas las API keys comprometidas
3. ✅ Implementar autenticación JWT
4. ✅ Agregar rate limiting
5. ✅ Validar inputs y archivos
6. ✅ Restringir CORS

### Fase 2: Arquitectura (Importante - Semana 2-3)
7. Refactorizar `generation.py` en módulos
8. Crear capa de repositorios
9. Implementar dependency injection
10. Extraer helpers reutilizables
11. Separar componentes del frontend

### Fase 3: Calidad (Necesario - Semana 3-4)
12. Configurar pytest + tests unitarios
13. Configurar ruff + eslint + pre-commit
14. Completar type hints
15. Migrar prints a logging
16. Escribir README.md completo

### Fase 4: Infraestructura (Deseable - Semana 5+)
17. Dockerizar la aplicación
18. Configurar CI/CD con GitHub Actions
19. Implementar caché con Redis
20. Agregar monitoreo básico
21. Paralelizar generación de imágenes

---

## 📊 Resumen

| Categoría | Críticos | Altos | Medios | Bajos |
|-----------|----------|-------|--------|-------|
| Seguridad | 2 | 2 | 2 | 0 |
| Arquitectura | 0 | 3 | 3 | 0 |
| Documentación | 0 | 1 | 2 | 1 |
| Calidad | 0 | 1 | 4 | 0 |
| Rendimiento | 0 | 0 | 3 | 1 |
| Infraestructura | 0 | 0 | 4 | 0 |
| **Total** | **2** | **7** | **18** | **2** |
