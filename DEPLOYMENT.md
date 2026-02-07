# 🚀 Checklist de Deployment - HeyMake

## ✅ Completado
- [x] Código subido a GitHub: https://github.com/diegoparma/heymake.git
- [x] Servicios de imagen arreglados (Higgsfield + Gemini)
- [x] Configuraciones de deployment creadas (vercel.json, render.yaml)
- [x] Documentación actualizada (README.md)
- [x] Variables de entorno documentadas (.env.example)

## 🎯 Próximos pasos para deployment

### Opción A: Vercel (Frontend) + Render (Backend) [RECOMENDADO]

#### 1. Deploy Backend en Render
1. **Crear cuenta en Render** (si no la tienes): https://render.com
2. **Crear nuevo Web Service**:
   - Repository: `https://github.com/diegoparma/heymake.git`
   - Branch: `main`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Python Version: `3.12`

3. **Configurar Variables de Entorno en Render**:
   ```
   TURSO_DATABASE_URL=libsql://tu-database.turso.io
   TURSO_AUTH_TOKEN=tu-turso-auth-token
   GEMINI_API_KEY=tu-gemini-api-key
   HIGGSFIELD_API_URL=https://platform.higgsfield.ai
   HIGGSFIELD_KEY_ID=tu-higgsfield-key-id
   HIGGSFIELD_SECRET=tu-higgsfield-secret
   OPENAI_API_KEY=tu-openai-api-key
   ```

#### 2. Deploy Frontend en Vercel
1. **Crear cuenta en Vercel** (si no la tienes): https://vercel.com
2. **Importar proyecto**:
   - Repository: `https://github.com/diegoparma/heymake.git`
   - Framework Preset: `Next.js`
   - Root Directory: `frontend`

3. **Configurar Variables de Entorno en Vercel**:
   ```
   NEXT_PUBLIC_API_URL=https://tu-app.onrender.com
   ```
   (Reemplaza `tu-app.onrender.com` con la URL que te dé Render)

### Opción B: Todo en Render (Alternativa)

1. **Usar render.yaml** (ya incluido en el proyecto)
2. **Fork del repositorio** en tu cuenta de GitHub
3. **Conectar Render con el repositorio**
4. **Configurar las mismas variables de entorno** listadas arriba

## 🔧 Variables de Entorno Críticas

### Para obtener las API Keys:

1. **Turso Database**:
   - Crear cuenta en https://turso.tech
   - Crear nueva database
   - Copiar Database URL y Auth Token

2. **Google Gemini**:
   - Ir a https://makersuite.google.com/app/apikey
   - Crear nueva API key

3. **Higgsfield** (opcional, si tienes créditos):
   - Tu Key ID y Secret actual

4. **OpenAI** (opcional):
   - Ir a https://platform.openai.com/api-keys
   - Crear nueva API key

## ⚠️ Importante ANTES del deployment

1. **Verificar que tienes créditos** en al menos uno de los servicios de imagen (actualmente Higgsfield dice "no credits" y Gemini tiene quota exhausted)

2. **Configurar Turso para producción**:
   - Crear una database nueva para producción
   - Ejecutar migraciones si es necesario

3. **Testear localmente** con las variables de producción:
   ```bash
   # En /backend
   cp ../.env.example .env
   # Editar .env con los valores reales
   python main.py
   
   # En /frontend  
   export NEXT_PUBLIC_API_URL=http://localhost:8000
   npm run dev
   ```

## 🎉 Después del deployment

1. **Verificar que ambos services funcionen**
2. **Testear la generación de imágenes** 
3. **Revisar logs** en las consolas de Vercel/Render
4. **Configurar dominio personalizado** (opcional)

## 🆘 Si algo falla

1. **Revisar logs** en las consolas de deployment
2. **Verificar variables de entorno**
3. **Comprobar que las APIs respondan**
4. **Revisar los errores específicos** en el frontend (ahora se muestran correctamente)

---

**¿Todo listo?** ¡Solo tienes que seguir los pasos de "Próximos pasos para deployment" y estarás en producción!