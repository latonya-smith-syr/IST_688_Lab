import streamlit as st

st.set_page_config(
    page_title="Lab Landing Page",
    layout="wide",
    initial_sidebar_state= 'expanded'

)
#welcome_page = st.Page('')
lab_01 = st.Page('Pages/lab_01.py', title="Lab 1")
lab_02 = st.Page('Pages/lab_02.py', title = "Lab 2")
lab_03 = st.Page('Pages/lab_03.py', title= "Lab 3", default=True)

pg = st.navigation([lab_01, lab_02, lab_03])
st.set_page_config(page_title='Lab Manager')
pg.run()