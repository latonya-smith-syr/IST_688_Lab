import streamlit as st

st.set_page_config(
    page_title="Lab Landing Page",
    layout="wide",
    initial_sidebar_state= 'expanded'

)
#welcome_page = st.Page('')
lab_01 = st.Page('Pages/lab_01.py', title="Lab 1")
lab_02 = st.Page('Pages/lab_02.py', title = "Lab 2", default=True)

pg = st.navigation([lab_01, lab_02])
st.set_page_config(page_title='Lab Manager')
pg.run()