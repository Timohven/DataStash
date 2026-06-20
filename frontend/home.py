import streamlit as st
from frontend.note_editor import note_editor
from frontend.note_display import display_note
from frontend.icons import ADD


hub = st.session_state.hub
user = st.session_state.user

st.title(f"Welcome, {user.username}!")
if st.button(f'{ADD} Note', type='primary'):
    note_editor(hub, user)
notes = hub.note_service.get_notes_by_author(user.username)
if len(notes) == 0:
  st.info("You haven't written any notes yet.")
else:
  for note in notes:
    display_note(note)