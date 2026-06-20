import streamlit as st
# from backend.database import Database
from backend.hub import Hub
from frontend.pages import pages


if 'hub' not in st.session_state:
  st.session_state.hub = Hub()
  
if 'logged_in' in st.session_state and st.session_state.logged_in:
  page = st.navigation([pages['home'], pages['logout']])
else:
  page = st.navigation([pages['login'], pages['signup']])

if __name__ == '__main__':
    page.run()

    # st.title('Notes app')
    #
    # database = Database()
    # query_results = database.execute_query('SELECT * FROM notes')
    # st.write(query_results)

    # Загрузит историю пары USD/UAH за последние 5 лет
    # data = yf.download("USDUAH=X", period="5y", interval="1d")
    # print(data[1:100])
