import streamlit as st
from frontend.note_editor import note_editor
from frontend.icons import CALENDAR, CLOCK, EDIT, DELETE


hub = st.session_state.hub
user = st.session_state.user

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


def display_note(note):
    with st.container(border=True):
        cols = st.columns([2, 5, 1, 1, 1])
        created_col, text_col, type_col, edit_col, delete_col = cols

        created_col.markdown(get_note_created_display(note))
        text_col.markdown(get_note_text_display(note))
        type_col.markdown(get_note_type_display(note))
        with edit_col:
            edit_button(note)
        with delete_col:
            delete_button(note)