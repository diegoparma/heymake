# HeyMake 🎬

Plataforma de generación de trailers con IA - Transforma guiones en trailers visuales usando modelos de IA de última generación.

## 🚀 Features

- **Análisis de Guiones**: Convierte scripts en escenas estructuradas usando LLM
- **Generación de Imágenes**: Múltiples proveedores (Gemini, Higgsfield, DALL-E, AIMLAPI)
- **Animación de Videos**: Convierte imágenes en videos con Kling AI y Google Veo
- **Streaming en Tiempo Real**: Progress tracking con Server-Sent Events
- **Reference Prompts**: Sistema de prompts de referencia para consistencia visual

## 🛠 Tech Stack

### Backend
- **FastAPI** (Python 3.12) - API REST
- **Turso** (LibSQL) - Base de datos
- **Redis** - Cache y sessions
- **Multiple AI APIs**:
  - OpenAI GPT-4 (LLM + DALL-E)
  - Google Gemini (LLM + Imagen)
  - Higgsfield (Flux)
  - AIMLAPI (Flux + otros modelos)
  - Kling AI (Video)
  - Google Veo (Video)

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Server-Sent Events** - Real-time updates

## 📁 Estructura del Proyecto

```
heyai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── core/           # Configuración
│   │   ├── schemas/        # Pydantic models
│   │   └── services/       # Business logic
│   ├── main.py             # Entry point
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/app/           # App router
│   ├── public/            # Static assets
│   └── package.json       # Node dependencies
└── README.md              # This file
```

## 🔧 Setup Local

### Prerequisites

- Python 3.12+
- Node.js 18+
- Redis server
- API keys (ver Variables de Entorno)

### 1. Clonar repositorio

```bash
git clone https://github.com/diegoparma/heymake.git
cd heymake
```

### 2. Backend Setup

```bash
cd backend

# Crear virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar
python main.py
```

Backend corriendo en: http://localhost:8000

### 3. Frontend Setup

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev
```

Frontend corriendo en: http://localhost:3000

## 🔑 Variables de Entorno

Crear archivo `backend/.env` con estas variables:

```env
# App
SECRET_KEY="your-secret-key-here"
ENV="development"

# Database - Turso
DATABASE_URL="your-turso-database-url"
DATABASE_AUTH_TOKEN="your-turso-auth-token"

# Redis
REDIS_URL="redis://localhost:6379"

# LLM Services
OPENAI_API_KEY="your-openai-key"
GOOGLE_AI_API_KEY="your-google-ai-key"
LLM_PROVIDER="openai"
LLM_MODEL="gpt-4-turbo-preview"

# Image Generation
HIGGSFIELD_API_KEY_ID="your-higgsfield-id"
HIGGSFIELD_API_KEY_SECRET="your-higgsfield-secret"
HIGGSFIELD_API_URL="https://platform.higgsfield.ai"

# Video Generation
KLING_API_KEY="your-kling-key"

# Storage
GOOGLE_DRIVE_CREDENTIALS_FILE="credentials.json"
```

### Donde conseguir API Keys:

- **OpenAI**: https://platform.openai.com/api-keys
- **Google AI**: https://aistudio.google.com/app/apikey
- **Higgsfield**: https://cloud.higgsfield.ai (requiere créditos)
- **Kling AI**: https://klingai.com/

## 🚀 Deployment

### Opción 1: Vercel (Frontend) + Render (Backend)

#### Frontend en Vercel:
1. Push código a GitHub
2. Conectar repositorio en Vercel
3. Configurar build:
   ```
   Framework: Next.js
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: .next
   ```

#### Backend en Render:
1. Crear Web Service en Render
2. Conectar repositorio GitHub
3. Configurar:
   ```
   Environment: Python 3
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   ```
4. Agregar variables de entorno en Render dashboard

### Opción 2: Todo en Render

Ver `render.yaml` para configuración completa.

## 📚 API Documentation

Una vez ejecutando, la documentación interactiva está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints principales:

- `POST /api/v1/generation/analyze-script` - Analizar guión
- `GET /api/v1/generation/generate-images-stream/{project_id}` - Generar imágenes (SSE)
- `POST /api/v1/generation/animate-scene` - Animar escena individual

## 🐛 Troubleshooting

### Backend no inicia
- Verificar que Redis esté corriendo
- Revisar API keys en `.env`
- Verificar versión de Python (3.12+)

### Frontend no conecta con Backend
- Verificar que backend esté en puerto 8000
- Revisar configuración de CORS en `main.py`

### Errores de generación
- Verificar créditos en APIs (Higgsfield)
- Revisar quotas (Google AI)
- Ver logs en `/tmp/backend.log`

## 🔒 Security Notes

- **Nunca** commitir archivos `.env` con API keys
- Rotar API keys regularmente
- Usar variables de entorno en producción
- Implementar autenticación antes de producción

## 📈 Performance

- Redis para caching (no implementado aún)
- Optimización de imágenes con Pillow
- Compresión de assets estáticos
- Rate limiting en endpoints críticos

## 🤝 Contributing

1. Fork el repositorio
2. Crear feature branch (`git checkout -b feature/amazing-feature`)
3. Commit cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la branch (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

## 📄 License

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Support

Si encontrás problemas o tenés preguntas:

1. Revisar [Issues existentes](https://github.com/diegoparma/heymake/issues)
2. Crear un [nuevo Issue](https://github.com/diegoparma/heymake/issues/new)
3. Incluir logs y configuración (sin API keys)

---

Hecho con ❤️ usando FastAPI y Next.js
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
