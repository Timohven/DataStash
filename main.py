import streamlit as st
from backend.hub import Hub
from core.db.sqlalchemy_db import Database
from frontend.pages import pages


if 'hub' not in st.session_state:
    database = Database(engine=st.connection("notesconn", type="sql").engine)
    st.session_state.hub = Hub(database=database)
  
if 'logged_in' in st.session_state and st.session_state.logged_in:
  page = st.navigation([pages['home'], pages['logout']])
else:
  page = st.navigation([pages['login'], pages['signup']])

if __name__ == '__main__':
    page.run()
