# core/config.py
from pathlib import Path

# Корень проекта — всегда знаем где он
PROJECT_ROOT = Path(r'C:\Users\ukrse\PROJECTS\DataStash')

# Папки для файлов
UPLOAD_DIR    = PROJECT_ROOT / 'uploads'
THUMBNAIL_DIR = UPLOAD_DIR / 'thumbnails'

# Подпапки по типам
TYPE_DIRS = {
    'photo': UPLOAD_DIR / 'photo',
    'video': UPLOAD_DIR / 'video',
    'pdf':   UPLOAD_DIR / 'pdf',
    'file':  UPLOAD_DIR / 'file',
}