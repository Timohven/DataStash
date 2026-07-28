import os
import streamlit as st
from pathlib import Path

from frontend.note_editor import note_editor
from frontend.icons import CALENDAR, CLOCK, EDIT, DELETE

from core.utils.thumbnail import get_thumbnail_path


hub = st.session_state.hub
user = st.session_state.user

# Типы заметок которые имеют файл на диске
FILE_TYPES = {'photo', 'video', 'pdf', 'file'}


def get_note_created_display(note):
    day = note.created_at.strftime('%Y-%m-%d')
    time = note.created_at.strftime('%H:%M')
    return f':gray[{CALENDAR} {day}  \n {CLOCK} {time}]'


def get_note_text_display(note):
    display_text = note.text.replace('\n', '  \n')
    return f':green[{display_text}]'


def get_note_type_display(note):
    display_type = note.note_type#.replace('\n', '  \n')
    return f':green[{display_type}]'


def edit_button(note):
    if st.button(f'{EDIT}', key=f"edit_{note.note_id}"):
        note_editor(hub, user, note)


def delete_button(note):
    if st.button(f'{DELETE}', key=f"delete_{note.note_id}"):
        deleted_note = hub.note_service.delete_note(note.note_id)
        if deleted_note:
            st.rerun()
        else:
            st.error("Failed to delete note.")


def display_thumbnail(note):
    """Показывает превью для файловых заметок."""
    thumbnail_path = get_thumbnail_path(note.text)
    print(f'thumbnail_path: {thumbnail_path}')
    if os.path.exists(thumbnail_path):
        st.image(thumbnail_path, width=80)
    else:
        # Иконка-заглушка если превью нет
        icons = {
            'photo': '🖼️',
            'video': '🎬',
            'pdf':   '📄',
            'file':  '📎',
        }
        st.markdown(f"### {icons.get(note.note_type, '📎')}")


def display_file_opener(note):
    """Кнопка для открытия файла в браузере."""
    from core.config import UPLOAD_DIR

    filename = Path(note.text).name
    note_path = Path(note.text)
    parts = note_path.parts

    type_folders = {'photo', 'video', 'pdf', 'file'}
    type_idx = next(
        (i for i, p in enumerate(parts) if p in type_folders),
        None
    )

    if type_idx is not None:
        file_path = UPLOAD_DIR / Path(*parts[type_idx:])
    else:
        file_path = UPLOAD_DIR / note_path.name

    if file_path.exists():
        with open(file_path, 'rb') as f:
            st.download_button(
                label=f'⬇️ {filename}',
                data=f,
                file_name=filename,
                key=f"download_{note.note_id}",
            )
    else:
        st.caption('Файл не найден')


def display_note(note):
    with st.container(border=True):
        if note.note_type in FILE_TYPES:
            # Для файловых заметок — превью + инфо + кнопки
            cols = st.columns([1, 2, 5, 1, 1, 1])
            preview_col, created_col, content_col, type_col, edit_col, delete_col = cols

            with preview_col:
                display_thumbnail(note)

            created_col.markdown(get_note_created_display(note))

            with content_col:
                display_file_opener(note)

            type_col.markdown(get_note_type_display(note))

            with edit_col:
                edit_button(note)

            with delete_col:
                delete_button(note)
        else:
            # Для текста и ссылок — как раньше
            cols = st.columns([2, 5, 1, 1, 1])
            created_col, text_col, type_col, edit_col, delete_col = cols

            created_col.markdown(get_note_created_display(note))
            text_col.markdown(get_note_text_display(note))
            type_col.markdown(get_note_type_display(note))

            with edit_col:
                edit_button(note)

            with delete_col:
                delete_button(note)
