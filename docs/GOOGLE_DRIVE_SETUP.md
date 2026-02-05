# Guía de Google Drive API Setup

## Paso 1: Crear Proyecto en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Google Drive API**

## Paso 2: Crear Service Account

1. Ve a **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Completa el formulario:
   - Name: `heyai-storage`
   - Description: `Service account for HeyAI file storage`
4. Click **Create and Continue**
5. Asigna el rol: **Editor** (o personalizado)
6. Click **Done**

## Paso 3: Generar Credenciales

1. Click en el service account creado
2. Ve a la pestaña **Keys**
3. Click **Add Key** > **Create new key**
4. Selecciona **JSON**
5. Descarga el archivo

## Paso 4: Configurar en el Proyecto

1. Renombra el archivo descargado a `credentials.json`
2. Muévelo a la carpeta `backend/`
3. Agrega `credentials.json` al `.gitignore` (ya está incluido)

## Paso 5: Crear Carpeta en Google Drive

1. Ve a [Google Drive](https://drive.google.com/)
2. Crea una carpeta llamada `HeyAI Projects`
3. Haz click derecho > **Share**
4. Comparte con el email del service account (en el JSON)
5. Dale permisos de **Editor**
6. Copia el ID de la carpeta de la URL:
   ```
   https://drive.google.com/drive/folders/[ESTE_ES_EL_ID]
   ```

## Paso 6: Configurar Variables de Entorno

En tu archivo `.env`:

```env
STORAGE_PROVIDER=gdrive
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_FOLDER_ID=tu_folder_id_aqui
```

## Verificar Setup

```bash
cd backend
python -c "
from app.services.storage_service import storage_service
print('✅ Google Drive configurado correctamente')
"
```

## Troubleshooting

### Error: "Credentials file not found"
- Verifica que `credentials.json` esté en la carpeta `backend/`
- Verifica el path en `.env`

### Error: "Permission denied"
- Verifica que hayas compartido la carpeta con el service account
- Verifica que el email del service account sea correcto

### Error: "API not enabled"
- Habilita Google Drive API en Cloud Console
- Puede tomar unos minutos en activarse

## Estructura Recomendada

```
Google Drive/
└── HeyAI Projects/          <- Carpeta compartida con service account
    ├── Project-ABC123/
    │   ├── images/
    │   ├── clips/
    │   └── final/
    └── Project-XYZ789/
        ├── images/
        ├── clips/
        └── final/
```

## Costos

- Google Drive API es **GRATIS** para uso normal
- Con Google Workspace: almacenamiento ilimitado
- Con cuenta gratuita: 15GB compartidos con Gmail

## Alternativas

Si prefieres no usar Google Drive:

1. **Local Storage** (desarrollo):
   ```env
   STORAGE_PROVIDER=local
   ```

2. **AWS S3** (futuro):
   - Más control
   - Mejor para producción
   - Requiere configuración adicional
