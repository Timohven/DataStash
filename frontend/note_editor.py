import streamlit as st


# Define your options matching the DB constraints
type_options = ['text', 'ref', 'pic', 'pdf', 'video']

hub = st.session_state.hub
@st.dialog("Note editor", width="large")
def note_editor(hub, user, note=None):
    # Find where the stored type lives in the list (default to 0 if not found)
    if note:
        default_index = type_options.index(note.note_type) if note.note_type in type_options else 0
    else:
        default_index = 0
    note_type = st.selectbox('Chose a note type', options=['text', 'ref', 'pic', 'pdf', 'video'], index=default_index)
    default_text = note.text if note else ''
    note_text = st.text_area('Enter a note', value=default_text)
    if st.button('Save note', type='primary'):
        if note:
            new_note = hub.note_service.update_note(note.note_id, note_type, note_text)
        else:
            new_note = hub.note_service.create_note(user.username, note_type, note_text)
        if new_note:
            st.success('Note saved successfully!')
            st.rerun()
        else:
            st.error('Failed to save note')