import streamlit as st


# Define your options matching the DB constraints
TYPE_OPTIONS = ['text', 'link', 'photo', 'file', 'video', 'pdf']

hub = st.session_state.hub



def _tag_selector(hub, selected_names: list[str]) -> list[str]:
    """Виджет выбора тегов — используется и при создании и при редактировании."""
    all_tags = hub.tag_service.get_all_tags()

    st.markdown('**Теги:**')

    # Поле для нового тега
    col1, col2 = st.columns([4, 1])
    with col1:
        new_tag = st.text_input('Новый тег', placeholder='Введите название...', label_visibility='collapsed')
    with col2:
        if st.button('+ Добавить'):
            if new_tag.strip():
                hub.tag_service.get_or_create_tag(new_tag.strip())
                st.rerun()

    # Чекбоксы для всех существующих тегов
    result = []
    if all_tags:
        cols = st.columns(3)  # теги в три колонки
        for i, tag in enumerate(hub.tag_service.get_all_tags()):
            with cols[i % 3]:
                if st.checkbox(tag.name, value=tag.name in selected_names, key=f"new_tag_{tag.tag_id}"):
                    result.append(tag.name)
    else:
        st.caption('Тегов пока нет — создайте первый')

    return result


@st.dialog("Note editor", width="large")
def note_editor(hub, user, note=None):
    if note:
        # Редактирование существующей заметки — как раньше
        if note.note_type in {'photo', 'video', 'pdf', 'file'}:
            st.caption(f'Тип заметки: **{note.note_type}** (нельзя изменить)')
            note_type = note.note_type
        else:
            note_type = st.selectbox(
                'Тип заметки',
                options=['text', 'link'],
                index=['text', 'link'].index(note.note_type) if note.note_type in ['text', 'link'] else 0,
            )

        default_text = note.text if note else ''
        note_text = st.text_area('Текст заметки', value=default_text, height=200)

        st.divider()

        # Текущие теги заметки
        current_tags = hub.tag_service.get_tags_for_note(note.note_id)
        current_names = [t.name for t in current_tags]
        selected_names = _tag_selector(hub, current_names)

        if st.button('Сохранить', type='primary'):
            new_note = hub.note_service.update_note(note.note_id, note_type, note_text)
            if new_note:
                st.success('Заметка сохранена!')
                st.rerun()
            else:
                st.error('Ошибка при сохранении')
    else:
        # Создание новой заметки
        tab_text, tab_file = st.tabs(['📝 Текст', '📎 Файл'])

        with tab_text:
            note_type = st.selectbox('Тип', options=['text', 'link'])
            note_text = st.text_area('Текст заметки', height=150)

            st.divider()
            selected_names = _tag_selector(hub, [])

            if st.button('Сохранить', type='primary', key='save_text'):
                if note_text.strip():
                    new_note = hub.note_service.create_note(user.username, note_type, note_text)
                    if new_note:
                        hub.tag_service.set_tags_for_note(new_note.note_id, selected_names)
                        st.success('Заметка сохранена!')
                        st.rerun()
                    else:
                        st.error('Ошибка при сохранении')
                else:
                    st.warning('Введите текст заметки')

        with tab_file:
            uploaded_file = st.file_uploader(
                'Выберите файл',
                type=['jpg', 'jpeg', 'png', 'gif', 'webp',  # фото
                      'mp4', 'mov', 'avi', 'mkv',            # видео
                      'pdf',                                  # pdf
                      'doc', 'docx', 'xls', 'xlsx', 'zip'],  # файлы
            )

            if uploaded_file:
                # Показываем превью для фото
                if uploaded_file.type.startswith('image/'):
                    st.image(uploaded_file, width=200)

                if st.button('Сохранить', type='primary', key='save_file'):
                    _save_uploaded_file(hub, user, uploaded_file)


def _save_uploaded_file(hub, user, uploaded_file, tag_names: list[str]):
    """Сохраняет загруженный файл и создаёт заметку с тегами."""
    import os
    import shutil
    from pathlib import Path
    from core.utils.type_detector import detect_type
    from core.utils.thumbnail import generate_thumbnail
    from api.routers.notes import sanitize_filename  # ← переиспользуем функцию

    # upload_dir = os.environ.get('UPLOAD_DIR', './uploads')
    from core.config import UPLOAD_DIR

    # Определяем тип и санируем имя
    safe_filename = sanitize_filename(uploaded_file.name)
    note_type = detect_type(filename=uploaded_file.name)

    # Сохраняем файл
    type_dir = Path(UPLOAD_DIR) / note_type
    type_dir.mkdir(parents=True, exist_ok=True)
    file_path = type_dir / safe_filename

    with open(file_path, 'wb') as f:
        shutil.copyfileobj(uploaded_file, f)

    # Генерируем превью
    generate_thumbnail(str(file_path), note_type)

    # Создаём заметку в БД
    new_note = hub.note_service.create_note(user.username, note_type, str(file_path))
    if new_note:
        hub.tag_service.set_tags_for_note(new_note.note_id, tag_names)
        st.success('Файл сохранён!')
        st.rerun()
    else:
        st.error('Ошибка при сохранении')
