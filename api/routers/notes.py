"""
api/routers/notes.py

CRUD для заметок — под реальный NoteService:
  GET /files/{file_path:path}
  GET /thumbnails/{file_path:path}

  POST   /upload             —  загрузить файл заметки

  POST   /notes              — создать заметку
  GET    /notes              — все заметки текущего пользователя
  PUT    /notes/{note_id}    — обновить заметку
  DELETE /notes/{note_id}    — удалить заметку
"""
from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_hub
from api.middleware.auth import get_current_username
from api.schemas.note import NoteCreate, NoteUpdate, NoteResponse
from core.hub import Hub
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
import shutil
import os
from fastapi.responses import FileResponse
from pathlib import Path
from core.utils.type_detector import detect_type
from core.utils.thumbnail import generate_thumbnail, get_thumbnail_path


UPLOAD_DIR = os.environ.get('UPLOAD_DIR', './uploads')
router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/files/{file_path:path}")
async def get_file(
    file_path: str,
    username: str = Depends(get_current_username),
):
    """
    Отдаёт файл по пути.
    file_path — относительный путь от корня проекта.
    Например: uploads/photo/IMG_001.jpg
    """
    full_path = Path(file_path)
    print(f'LOOKING FOR: {full_path.absolute()}')  # ← покажет полный путь

    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    return FileResponse(
        path=full_path,
        filename=full_path.name,  # имя файла в заголовке Content-Disposition
    )

@router.post("/upload", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def upload_note(
    file: UploadFile = File(...),
    hub: Hub = Depends(get_hub),
    username: str = Depends(get_current_username),
):
    """
    Принимает файл (фото или любой файл) через multipart/form-data.
    Определяет тип, сохраняет файл, создаёт заметку.
    """
    # Определяем тип по имени файла
    note_type = detect_type(filename=file.filename)

    # Сохраняем файл на диск
    type_dir = os.path.join(UPLOAD_DIR, note_type)   # uploads/photo/ или uploads/file/
    os.makedirs(type_dir, exist_ok=True)

    file_path = os.path.join(type_dir, file.filename)
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Генерируем превью асинхронно (не блокируем ответ)
    thumbnail_path = generate_thumbnail(file_path, note_type)
    print(f'THUMBNAIL: {thumbnail_path}')

    # Создаём заметку — в text сохраняем путь к файлу
    note = hub.note_service.create_note(
        author=username,
        note_type=note_type,
        note_text=file_path,
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to create note',
        )
    return note

@router.get("/thumbnails/{file_path:path}")
async def get_thumbnail(
        file_path: str,
        username: str = Depends(get_current_username),
):
    thumbnail_path = get_thumbnail_path(file_path)

    if not os.path.exists(thumbnail_path):
        raise HTTPException(status_code=404, detail="Thumbnail not found")

    return FileResponse(path=thumbnail_path, media_type='image/jpeg')

@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    hub: Hub = Depends(get_hub),
    username: str = Depends(get_current_username),
):
    note = hub.note_service.create_note(
        author=username,
        note_type=payload.note_type,
        note_text=payload.note_text,
    )
    if note is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create note")
    return note


@router.get("", response_model=list[NoteResponse])
def list_my_notes(
    hub: Hub = Depends(get_hub),
    username: str = Depends(get_current_username),
):
    return hub.note_service.get_notes_by_author(username)


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    payload: NoteUpdate,
    hub: Hub = Depends(get_hub),
    username: str = Depends(get_current_username),
):
    # Проверяем что заметка существует и принадлежит текущему пользователю
    # через get_notes_by_author — ищем нужную среди заметок пользователя
    notes = hub.note_service.get_notes_by_author(username)
    existing = next((n for n in notes if n.note_id == note_id), None)

    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or not yours",
        )

    updated = hub.note_service.update_note(
        note_id=note_id,
        note_type=payload.note_type,
        note_text=payload.note_text,
    )
    return updated


@router.delete("/{note_id}", response_model=NoteResponse)
def delete_note(
    note_id: int,
    hub: Hub = Depends(get_hub),
    username: str = Depends(get_current_username),
):
    # Проверяем владельца перед удалением
    notes = hub.note_service.get_notes_by_author(username)
    existing = next((n for n in notes if n.note_id == note_id), None)

    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or not yours",
        )

    # NoteService сам удалит файл и превью
    deleted = hub.note_service.delete_note(note_id)
    return deleted