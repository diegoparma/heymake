# HeyAI - Plataforma de Generación de Trailers

Plataforma para crear trailers de películas y publicidades a partir de ideas o guiones usando IA.

## 🎬 Características

- **Análisis de Guión con LLM**: Convierte ideas y guiones en escenas detalladas
- **Generación de Imágenes**: Integración con Higgsfield AI para crear storyboards
- **Procesamiento de Video**: Ensamblaje automático de clips y efectos
- **Gestión de Assets**: Sistema completo para organizar imágenes y videos

## 🏗️ Arquitectura

```
├── backend/          # FastAPI - Python
├── frontend/         # Next.js - TypeScript
├── docs/             # Documentación
└── docker-compose.yml
```

## 🚀 Stack Tecnológico

### Backend
- **FastAPI**: Framework web asíncrono
- **Turso (LibSQL)**: Base de datos SQLite serverless
- **Redis**: Cache y colas de procesamiento
- **Celery**: Procesamiento asíncrono de tareas
- **OpenAI/Anthropic**: LLMs para análisis de guiones
- **Higgsfield AI**: Generación de imágenes
- **Kling AI**: Animación de imágenes a video
- **Google Drive API**: Storage y gestión de archivos

### Frontend
- **Next.js 14**: Framework React con App Router
- **TypeScript**: Tipado estático
- **Tailwind CSS**: Estilos
- **Zustand**: Estado global
- **React Query**: Gestión de datos asíncronos

## 📦 Instalación

### Prerrequisitos

1. **Turso Database** (ver [docs/TURSO_SETUP.md](docs/TURSO_SETUP.md))
2. **Google Drive API** (ver [docs/GOOGLE_DRIVE_SETUP.md](docs/GOOGLE_DRIVE_SETUP.md))
3. **API Keys**:
   - OpenAI o Anthropic
   - Higgsfield AI
   - Kling AI (o Runway como alternativa)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configurar variables de entorno
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
# Configurar variables de entorno
npm run dev
```

## 🔧 Configuración

### 1. Turso Database
Ver guía detallada: [docs/TURSO_SETUP.md](docs/TURSO_SETUP.md)

```bash
# Instalar CLI
curl -sSfL https://get.tur.so/install.sh | bash

# Crear database
turso db create heyai
turso db tokens create heyai
```

### 2. Google Drive API
Ver guía detallada: [docs/GOOGLE_DRIVE_SETUP.md](docs/GOOGLE_DRIVE_SETUP.md)
x] v0.1: Backend base + integración LLM
- [x] v0.2: Integración Higgsfield para imágenes
- [x] v0.3: Integración Kling para animación
- [x] v0.4: Google Drive storage
- [ ] v0.5: Frontend básico
- [ ] v0.6: Sistema completo de generación
- [ ] v0.7: Workflow de aprobación
- [ ] v1.0: Release inicial
- [ ] v2.0: Ensamblaje automático (opcional)
### 3. API Keys
- **OpenAI/Anthropic**: Para análisis de guiones
- **Higgsfield**: Para generación de imágenes
- **Kling/Runway**: Para animación de videos

Ver [docs/KLING_SETUP.md](docs/KLING_SETUP.md) para alternativas.

## 📖 Documentación

Ver [docs/](./docs) para documentación detallada.

## 🎯 Roadmap

- [ ] v0.1: Backend base + integración LLM
- [ ] v0.2: Integración Higgsfield
- [ ] v0.3: Frontend básico
- [ ] v0.4: Procesamiento de video
- [ ] v0.5: Sistema completo de assets
- [ ] v1.0: Release inicial

## 📝 Licencia

MIT
