# 🚀 RENDER DEPLOYMENT - Configuración Manual

**IMPORTANTE**: No uses el `render.yaml` automático. Render lo detecta Dockerfiles y se confunde.

## 📋 **Pasos EXACTOS para deployment manual:**

### 1. **Backend Service (heymake-backend)**

**En render.com:**
1. New Web Service
2. Connect Repository: `https://github.com/diegoparma/heymake.git`
3. **CONFIGURACIÓN:**

| Campo | Valor |
|-------|-------|
| **Name** | `heymake-backend` |
| **Language** | `Python 3` |
| **Branch** | `main` |
| **Root Directory** | *(leave blank)* |
| **Build Command** | `cd backend && pip install -r requirements.txt` |
| **Start Command** | `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT` |

**Environment Variables:**
```
ENV=production
DEBUG=false
TURSO_DATABASE_URL=libsql://your-database.turso.io
TURSO_AUTH_TOKEN=your-auth-token
GEMINI_API_KEY=your-gemini-key
HIGGSFIELD_KEY_ID=your-higgsfield-id
HIGGSFIELD_SECRET=your-higgsfield-secret
HIGGSFIELD_API_URL=https://platform.higgsfield.ai
OPENAI_API_KEY=your-openai-key
CORS_ORIGINS=*
```

### 2. **Frontend Service (heymake-frontend)**

**En render.com:**
1. New Web Service (DESPUÉS de que backend esté listo)
2. Connect Repository: `https://github.com/diegoparma/heymake.git`
3. **CONFIGURACIÓN:**

| Campo | Valor |
|-------|-------|
| **Name** | `heymake-frontend` |
| **Language** | `Node` |
| **Branch** | `main` |
| **Root Directory** | *(leave blank)* |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Start Command** | `cd frontend && npm run start` |

**Environment Variables:**
```
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://heymake-backend.onrender.com
```
*(Reemplaza con la URL real de tu backend)*

### 3. **Redis Service (heymake-redis)**

1. New Redis service
2. Name: `heymake-redis`
3. Plan: Starter (free)

**Para conectar Redis al backend:**
- En el backend service, agregar variable:
- `REDIS_URL` = *(Copiar connection string de Redis service)*

## ❌ **LO QUE NO DEBES HACER:**
- ❌ No uses "Deploy from render.yaml"
- ❌ No selecciones Docker si aparece la opción
- ❌ No pongas rutas absolutas en Root Directory

## ✅ **LO QUE SÍ DEBES HACER:**
- ✅ Deploy manual paso a paso
- ✅ Usar `env: python` para backend
- ✅ Usar `env: node` para frontend  
- ✅ Comandos con `cd backend &&` y `cd frontend &&`

## 🔍 **Para verificar:**
1. **Backend health check:** `https://tu-backend.onrender.com/health`
2. **Frontend:** Debería cargar la página principal
3. **API docs:** `https://tu-backend.onrender.com/docs`

---

**¿Por qué falló antes?** Render detectó los Dockerfiles y trató de usar Docker automáticamente, pero el `render.yaml` decía `python`. Esta confusión causa el error.

**Los Dockerfiles están temporalmente deshabilitados** (`.disabled`) para evitar la auto-detección.