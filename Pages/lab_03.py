import streamlit as st
from openai import OpenAI

st.title("My Lab 3 question answering chatbot")

st.write("Hi! We will be using Chat-GPT for this bot")

model = "gpt-4o-mini"

if 'client' not in st.session_state:
    api_key = st.secrets["OPEN_API_KEY"]
    st.session_state.client= OpenAI(api_key=api_key)

if "messgaes" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]