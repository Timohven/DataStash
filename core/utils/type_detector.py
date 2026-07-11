# core/utils/type_detector.py
import re

# Типы заметок
class NoteType:
    TEXT  = 'text'
    LINK  = 'link'
    PHOTO = 'photo'
    FILE  = 'file'
    VIDEO = 'video'

# Расширения фото
PHOTO_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic', '.bmp'}

# Расширения  видео
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v'}

# Расширения файлов (не фото/видео)
FILE_EXTENSIONS  = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.txt', '.mp3'}

URL_PATTERN = re.compile(
    r'^(https?://)'           # http:// или https://
    r'[\w\-]+(\.[\w\-]+)+'   # домен
    r'([\w.,@?^=%&:/~+#\-_]*[\w@?^=%&/~+#\-_])?$',  # путь/параметры
    re.IGNORECASE
)


def detect_type(text: str = None, filename: str = None) -> str:
    """
    Определяет тип заметки.

    :param text:     текстовый контент (от Share Intent или ввода)
    :param filename: имя файла (если шарится файл/фото)
    :return:         одна из констант NoteType
    """
    # Если есть имя файла — определяем по расширению
    if filename:
        ext = _get_extension(filename)
        if ext in PHOTO_EXTENSIONS:
            return NoteType.PHOTO
        if ext in VIDEO_EXTENSIONS:
            return NoteType.VIDEO
        return NoteType.FILE  # всё остальное — файл

    # Если есть текст — проверяем на ссылку
    if text:
        stripped = text.strip()
        if URL_PATTERN.match(stripped):
            return NoteType.LINK

    return NoteType.TEXT  # по умолчанию — текст


def _get_extension(filename: str) -> str:
    """Возвращает расширение файла в нижнем регистре."""
    if '.' not in filename:
        return ''
    return '.' + filename.rsplit('.', 1)[-1].lower()