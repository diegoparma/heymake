# Guía de Desarrollo

## Setup Inicial

### 1. Clonar y Configurar

```bash
git clone <repo-url>
cd heyai
```

### 2. Backend Setup

```bash
cd backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Iniciar base de datos con Docker
docker run -d \
  --name heyai-postgres \
  -e POSTGRES_DB=heyai \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:16-alpine

docker run -d \
  --name heyai-redis \
  -p 6379:6379 \
  redis:7-alpine

# Iniciar servidor
uvicorn main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.local

# Iniciar servidor de desarrollo
npm run dev
```

### 4. Celery Worker (opcional para tareas asíncronas)

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

## Usando Docker Compose

La forma más fácil de iniciar todo:

```bash
docker-compose up -d
```

Esto iniciará:
- PostgreSQL (puerto 5432)
- Redis (puerto 6379)
- Backend API (puerto 8000)
- Celery Worker
- Frontend (puerto 3000)

## Estructura del Proyecto

```
heyai/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints REST
│   │   ├── core/         # Configuración
│   │   ├── models/       # Modelos de DB
│   │   ├── schemas/      # Schemas Pydantic
│   │   ├── services/     # Lógica de negocio
│   │   └── tasks/        # Tareas Celery
│   ├── main.py           # Entry point
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/          # Pages (App Router)
│   │   ├── components/   # Componentes React
│   │   ├── lib/          # Utilidades
│   │   └── types/        # TypeScript types
│   └── package.json
│
├── docs/                 # Documentación
└── docker-compose.yml
```

## APIs Disponibles

### Backend API (http://localhost:8000)

- `GET /` - Health check
- `GET /api/docs` - Documentación Swagger
- `GET /api/v1/projects` - Listar proyectos
- `POST /api/v1/projects` - Crear proyecto
- `GET /api/v1/projects/{id}` - Obtener proyecto
- `PATCH /api/v1/projects/{id}` - Actualizar proyecto
- `DELETE /api/v1/projects/{id}` - Eliminar proyecto

### Frontend (http://localhost:3000)

- `/` - Homepage
- `/projects` - Lista de proyectos
- `/projects/new` - Crear nuevo proyecto
- `/projects/{id}` - Detalle de proyecto

## Testing

### Backend

```bash
cd backend
pytest
```

### Frontend

```bash
cd frontend
npm test
```

## Despliegue

### Backend

- Render/Railway/Fly.io para FastAPI
- Supabase para PostgreSQL
- Upstash para Redis

### Frontend

- Vercel/Netlify para Next.js

## Variables de Entorno Requeridas

### Backend

```
OPENAI_API_KEY=sk-...
HIGGSFIELD_API_KEY=...
DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
```

### Frontend

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Troubleshooting

### Error de conexión a DB

- Verificar que PostgreSQL esté corriendo
- Revisar DATABASE_URL en .env

### Error de conexión a Redis

- Verificar que Redis esté corriendo
- Revisar REDIS_URL en .env

### Frontend no conecta al backend

- Verificar NEXT_PUBLIC_API_URL
- Verificar que CORS esté configurado en backend
