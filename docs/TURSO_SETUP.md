# Guía de Turso Database Setup

## ¿Qué es Turso?

Turso es una base de datos SQLite distribuida y serverless, perfecta para este proyecto:
- ⚡ Ultra rápido (edge-hosted)
- 🆓 Gratis para empezar (500 DBs, 9GB storage)
- 🌍 Réplicas globales automáticas
- 🔄 Sincronización en tiempo real
- 💪 Compatible con SQLAlchemy

## Paso 1: Instalar Turso CLI

### macOS/Linux
```bash
curl -sSfL https://get.tur.so/install.sh | bash
```

### Windows
```powershell
powershell -c "irm get.tur.so/install.ps1 | iex"
```

## Paso 2: Crear Cuenta y Autenticarse

```bash
# Signup/Login
turso auth signup

# O si ya tienes cuenta
turso auth login
```

## Paso 3: Crear Database

```bash
# Crear database para HeyAI
turso db create heyai

# Ver información de la database
turso db show heyai
```

Esto te dará:
- **URL**: `libsql://heyai-[tu-username].turso.io`
- **Location**: Nearest edge location

## Paso 4: Crear Auth Token

```bash
# Generar token de autenticación
turso db tokens create heyai

# Copia el token generado
```

## Paso 5: Configurar Variables de Entorno

En tu archivo `backend/.env`:

```env
# Turso Database
DATABASE_URL=libsql://heyai-tu-username.turso.io
DATABASE_AUTH_TOKEN=eyJhbGc...tu-token-aqui
DATABASE_ECHO=False
```

## Paso 6: Crear Tablas

```bash
cd backend

# Activar entorno virtual
source venv/bin/activate  # macOS/Linux
# o
venv\Scripts\activate  # Windows

# Iniciar la aplicación (creará las tablas automáticamente)
python -c "
import asyncio
from app.core.database import init_db
asyncio.run(init_db())
print('✅ Tablas creadas en Turso')
"
```

## Comandos Útiles

### Ver databases
```bash
turso db list
```

### Conectarse con shell
```bash
turso db shell heyai
```

Dentro del shell SQLite:
```sql
-- Ver tablas
.tables

-- Ver estructura de tabla
.schema projects

-- Ver datos
SELECT * FROM projects;

-- Salir
.quit
```

### Ver estadísticas
```bash
turso db show heyai --verbose
```

### Crear réplicas (opcional)
```bash
# Crear réplica en otra región
turso db replicate heyai --location syd  # Sydney
```

## Desarrollo Local

Para desarrollo local sin conexión a internet:

```env
# Usar SQLite local
DATABASE_URL=sqlite:///./heyai.db
DATABASE_AUTH_TOKEN=
```

## Migración de PostgreSQL a Turso

Si ya tienes datos en PostgreSQL:

1. **Export de PostgreSQL**:
```bash
pg_dump -d heyai > dump.sql
```

2. **Adaptar SQL para SQLite**:
   - Turso usa sintaxis SQLite
   - Algunos tipos de datos pueden cambiar
   - Secuencias → AUTOINCREMENT

3. **Import a Turso**:
```bash
turso db shell heyai < dump.sql
```

## Límites del Plan Gratuito

- 500 databases
- 9 GB de storage total
- 1 billion row reads/mes
- 25 million row writes/mes

Para la mayoría de proyectos esto es más que suficiente.

## Ventajas vs PostgreSQL

✅ **No necesitas Docker/servidor** para desarrollo
✅ **Edge-hosted**: Latencia ultra baja
✅ **Réplicas automáticas** en múltiples regiones
✅ **Backups automáticos**
✅ **Branching**: Crear copias para testing
✅ **Gratis para empezar**

## Troubleshooting

### Error: "Invalid auth token"
```bash
# Regenerar token
turso db tokens create heyai
```

### Error: "Database not found"
```bash
# Verificar que existe
turso db list
```

### Error de conexión
```bash
# Verificar que la URL sea correcta
turso db show heyai
```

## Recursos

- [Turso Docs](https://docs.turso.tech/)
- [Turso CLI Reference](https://docs.turso.tech/reference/turso-cli)
- [Pricing](https://turso.tech/pricing)
