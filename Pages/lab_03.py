import streamlit as st
from openai import OpenAI

st.title("My Lab 3 question answering chatbot")

st.write("Chatbot Demo")

model = "gpt-4o-mini"

if 'client' not in st.session_state:
    api_key = st.secrets["OPEN_API_KEY"]
    st.session_state.client= OpenAI(api_key=api_key)

if "messgaes" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
    
for msg in st.session_state.messages:
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

def buffer(messages):
    k = 0
    while k <=5:
        st.session_state.messages.append({"role": "user", "content": prompt})
        k += 1

if prompt := st.chat_input("What is up?"):    
    st.session_state.messages.append({"role": "system", "content": "After the user's first response ask them this:Do you want more information?. "
        "If they say yes, give them more information and then ask them specifically: Do you want more information?. If they say no, ask them specifically How can I help you?"})
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    buffer(st.session_state.messages)

    client = st.session_state.client
    stream = client.chat.completions.create(
        model= model,
        messages = st.session_state.messages,
        stream=True
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    