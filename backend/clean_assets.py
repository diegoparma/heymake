"""
Script para limpiar todos los assets de la base de datos
"""
import asyncio
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import TursoClient
from app.core.config import settings


async def clean_assets():
    client = TursoClient(settings.DATABASE_URL, settings.DATABASE_AUTH_TOKEN)
    
    # Contar assets existentes
    result = await client.execute('SELECT COUNT(*) as count FROM assets')
    count = result[0]['count'] if result else 0
    
    print(f'\n🗑️  Assets encontrados: {count}')
    
    if count == 0:
        print('   ✅ No hay assets para borrar')
        return
    
    # Borrar todos los assets
    print(f'   🔄 Borrando {count} assets...')
    await client.execute('DELETE FROM assets')
    print(f'   ✅ Assets borrados de la base de datos')
    
    # Limpiar archivos locales
    images_dir = Path("uploads/images")
    if images_dir.exists():
        image_files = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
        if image_files:
            print(f'\n📁 Archivos encontrados: {len(image_files)}')
            for img_file in image_files:
                img_file.unlink()
                print(f'   🗑️  Borrado: {img_file.name}')
            print(f'   ✅ Archivos locales borrados')
        else:
            print(f'\n📁 No hay archivos locales para borrar')
    
    print('\n✨ Limpieza completada!\n')


if __name__ == "__main__":
    asyncio.run(clean_assets())
