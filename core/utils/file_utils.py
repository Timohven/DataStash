# core/utils/file_utils.py
import re
import uuid
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    """
    Убирает пробелы и спецсимволы из имени файла.
    Оставляет только буквы, цифры, дефис и подчёркивание.
    Добавляет UUID чтобы избежать коллизий имён.
    """

    stem = Path(filename).stem
    ext = Path(filename).suffix.lower()
    # Заменяем пробелы и спецсимволы на подчёркивание
    clean = re.sub(r'[^\w\-]', '_', stem)
    # Убираем множественные подчёркивания
    clean = re.sub(r'_+', '_', clean).strip('_')
    # Добавляем UUID чтобы избежать коллизий
    unique = f'{clean}_{uuid.uuid4().hex[:8]}{ext}'
    return unique
