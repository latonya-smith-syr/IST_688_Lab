import streamlit as st

st.set_page_config(
    page_title="Lab Landing Page",
    layout="wide",
    initial_sidebar_state= 'expanded'

)

lab_01 = st.Page('Labs/lab_01.py', title="Lab 1")
lab_02 = st.Page('Labs/lab_02.py', title = "Lab 2")

pg = st.navigation([lab_01, lab_02])
st.set_page_config(page_title='Lab Manager')
pg.run()