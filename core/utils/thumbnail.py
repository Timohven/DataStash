"""
core/utils/thumbnail.py

Генерация превью для разных типов файлов.
Все превью сохраняются в uploads/thumbnails/ как JPEG.
"""
import os
from pathlib import Path
from PIL import Image

THUMBNAIL_SIZE = (200, 200)  # размер превью в пикселях
THUMBNAIL_DIR = os.environ.get('UPLOAD_DIR', './uploads') + '/thumbnails'


def get_thumbnail_path(original_path: str) -> str:
    """Возвращает путь к превью для данного файла."""
    filename = Path(original_path).stem  # имя без расширения
    return os.path.join(THUMBNAIL_DIR, f'{filename}.jpg')


def generate_thumbnail(file_path: str, note_type: str) -> str | None:
    """
    Генерирует превью и возвращает путь к нему.
    Возвращает None если генерация не поддерживается или не удалась.
    """
    os.makedirs(THUMBNAIL_DIR, exist_ok=True)
    thumbnail_path = get_thumbnail_path(file_path)

    # Если превью уже есть — не пересоздаём
    if os.path.exists(thumbnail_path):
        return thumbnail_path

    try:
        if note_type == 'photo':
            return _thumbnail_from_image(file_path, thumbnail_path)
        elif note_type == 'pdf':
            return _thumbnail_from_pdf(file_path, thumbnail_path)
        elif note_type == 'video':
            return _thumbnail_from_video(file_path, thumbnail_path)
        return None
    except Exception as e:
        print(f'Thumbnail generation failed for {file_path}: {e}')
        return None


def _thumbnail_from_image(file_path: str, thumbnail_path: str) -> str:
    with Image.open(file_path) as img:
        img.thumbnail(THUMBNAIL_SIZE)
        img.convert('RGB').save(thumbnail_path, 'JPEG')
    return thumbnail_path


def _thumbnail_from_pdf(file_path: str, thumbnail_path: str) -> str:
    from pdf2image import convert_from_path
    # pages = convert_from_path(file_path, first_page=1, last_page=1, dpi=72)
    import os

    print(f'PDF FILE EXISTS: {os.path.exists(file_path)}')
    print(f'PDF FILE PATH: {os.path.abspath(file_path)}')
    poppler = r'C:\poppler\Library\bin'
    print(f'POPPLER PATH EXISTS: {os.path.exists(poppler)}')
    # print(f'PDFTOPPM EXISTS: {os.path.exists(poppler + r"\pdftoppm.exe")}')
    try:
        pages = convert_from_path(
            file_path,
            first_page=1,
            last_page=1,
            dpi=72,
            poppler_path=r'C:\poppler\Library\bin'
        )
        if pages:
            img = pages[0]
            img.thumbnail(THUMBNAIL_SIZE)
            img.save(thumbnail_path, 'JPEG')
        return thumbnail_path
    except Exception as e:
        print(f'PDF THUMBNAIL ERROR: {e}')  # ← покажет точную ошибку
        raise


def _thumbnail_from_video(file_path: str, thumbnail_path: str) -> str:
    import ffmpeg
    (
        ffmpeg
        .input(file_path, ss=1)        # кадр на 1-й секунде
        .filter('scale', 200, -1)      # ширина 200px, высота пропорционально
        .output(thumbnail_path, vframes=1)
        .overwrite_output()
        .run(quiet=True, cmd=r'C:\ffmpeg\bin\ffmpeg.exe')  # ← явный путь
    )
    return thumbnail_path