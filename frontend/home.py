import streamlit as st
from frontend.note_editor import note_editor
from frontend.note_display import display_note
from frontend.icons import ADD


hub = st.session_state.hub
user = st.session_state.user

# Загружаем все теги
all_tags = hub.tag_service.get_all_tags()
tag_names = [t.name for t in all_tags]

# Фильтр вверху страницы
selected_tags = st.multiselect(
    'Фильтр по тегам',
    options=tag_names,
    default=[],
    placeholder='Все теги',
)

# st.title(f"Welcome, {user.username}!")
# Показываем статус фильтра
if selected_tags:
    st.caption(f'Активные теги: {", ".join(selected_tags)}')
else:
    st.caption('Все теги')

if st.button(f'{ADD} Note', type='primary'):
    note_editor(hub, user)
# notes = hub.note_service.get_notes_by_author(user.username)
# Получаем заметки с учётом фильтра
notes = hub.note_service.get_notes_by_author_and_tags(user.username, selected_tags)
if len(notes) == 0:
  st.info("You haven't written any notes yet.")
else:
  for note in notes:
    display_note(note)