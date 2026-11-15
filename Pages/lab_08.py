import requests
import streamlit as st
from openai import OpenAI
import json
import base64
from pathlib import Path


if "messages" not in st.session_state:
    st.session_state.messages = []
if "source" not in st.session_state:
    st.session_state.source = None        # image part or transcript text
    st.session_state.source_mode = None   # "Image" or "Audio"


st.title("See and Hear Assistant")

model = "gpt-4o-mini"

client = OpenAI(api_key=st.secrets["OPEN_API_KEY"])
mode = st.radio("Input type", ["Image", "Audio"], horizontal=True)
types = ["png", "jpg", "jpeg"] if mode == "Image" else ["mp3", "wav", "m4a"]
upload = st.file_uploader(f"Upload {mode.lower()}", type=types, key=f"upload_{mode}")
question = st.text_input("Question (optional)")



system_prompt = "Please give a short summary from this audio or video input and" \
"Also, provide 3 key points. If the user enters a question, use the information you gained from the uploaded material" \
"to answer the question. If the input can not be used or confirmed from the uploaded material, do not attempt to answer the question." \
"Acknowledge the fact that the information is not in the uploaded material. Treat the uploaded text as source material."


# if 'client' not in st.session_state:
#     api_key = st.secrets["OPEN_API_KEY"]
#     st.session_state.client = OpenAI(api_key=api_key)


def prepare_image(upload):
    formats = {".png": "image/png", ".jpg" : "image/jpeg",
               ".jpeg": "image/jpeg"}
    mime = formats[Path(upload.name).suffix.lower()]
    encoded = base64.b64encode(upload.getvalue()).decode("utf-8")
    return {"type": "input_image",
            "image_url": f"data:{mime};base64,{encoded}"}

def transcribe_audio(upload):
    transcript = client.audio.transcriptions.create(
        model="gpt-transcribe",
        file=(upload.name, upload.getvalue())
    ) 
    return transcript.text

def analyze_content(content, prompt):
    response = client.responses.create(
        model = model, instructions=prompt,
        input=[{"role": "user", "content": content}],
        max_output_tokens=600
    )
    return response.output_text

def history_text():
    # Turns the conversation so far into plain text for the prompt
    return "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages)

def build_content(text):
    if st.session_state.source_mode == "Image":
        return [
            {"type": "input_text", "text": text},
            st.session_state.source,
        ]
    return [
        {"type": "input_text",
         "text": f"Transcript:\n{st.session_state.source}\n\nQuestion: {text}"},
    ]

if st.button("Analyze"):
    if upload is None:
        st.warning("Please upload a file first.")
    else:
        with st.spinner("Please wait ..."):
            st.session_state.messages = []
            st.session_state.source_mode = mode
            if mode == "Image":
                st.session_state.source = prepare_image(upload)
            else:
                st.session_state.source = transcribe_audio(upload)

            first_question = question or "Summarize this."
            result = analyze_content(build_content(first_question), system_prompt)

        st.session_state.messages.append({"role": "user", "content": first_question})
        st.session_state.messages.append({"role": "assistant", "content": result})

if st.session_state.source_mode == "Audio" and st.session_state.source:
    with st.expander("Transcript"):
        st.write(st.session_state.source)


# --- Draw the conversation ---

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

if st.session_state.source is not None:
    if follow_up := st.chat_input("Ask a follow-up question"):
        # Build the prompt before adding the new question to history
        prompt = system_prompt + "\n\nConversation so far:\n" + history_text()

        with st.chat_message("user"):
            st.write(follow_up)

        with st.spinner("Please wait ..."):
            result = analyze_content(build_content(follow_up), prompt)

        with st.chat_message("assistant"):
            st.write(result)

        st.session_state.messages.append({"role": "user", "content": follow_up})
        st.session_state.messages.append({"role": "assistant", "content": result})


# """
# a. How do the image payload and audio transcription request differ?

# The image is sent directly to a vision model as base64 data alongside the text prompt in one 
# request, while the audio is first uploaded as a file to a separate transcription endpoint that returns text, 
# which is then sent to the model in a second step.


# b. What improved after your prompt revision? How did the app handle missing
# information?

# After revising the prompt, the responses became more specific and consistent, and when 
# information was missing the app stated that it wasn’t present instead of guessing.

# c. What can transcription lose from audio? What additional processing would video
# require?

# Transcription loses tone, emotion, emphasis, speaker identity, and non-speech sounds, 
# while video would also require extracting the audio, sampling frames, and aligning them by 
# timestamp.
# """