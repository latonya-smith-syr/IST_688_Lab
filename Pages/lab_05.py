import requests
import streamlit as st
from openai import OpenAI


st.title("What To Wear Bot")

model = "gpt-4o-mini"

if 'client' not in st.session_state:
    api_key = st.secrets["OPEN_API_KEY"]
    st.session_state.client= OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if 'client' not in st.session_state:
    api_key = st.secrets["OPEN_API_KEY"]
    st.session_state.client= OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

def get_current_weather(location):
    url = f'https://wttr.in/{location}?format=j1'
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception(f"wttr.in error:status {response.status_code}")
    try: 
        data = response.json()
    except ValueError:
        raise Exception(f"Could not find a location named{location}")
    current = data['current_condition'][0]


    return {
        'location':location,
        'temperature': float(current['temp_F']),
        'description': current['weatherDesc'][0]['value'],
        'FeelsLikeF': int(current['FeelsLikeF']),
        'visibility' : float(current['visibility']),
        'humidity' : int(current['humidity']),
        'uvIndex' : int(current['uvIndex']),
        'windspeedMiles': float(current['windspeedMiles'])
    }

tools = [
    {
    "type": "function",
        "function": {
        "name": "get_current_weather",
        "description": "Get the current weather",
        "parameters": {
            "type":"object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Fransico, CA",
                },
            },
        },
         "required": ["location"],
    },

}
]


if prompt := st.chat_input("I "):    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = st.session_state.client

    messages = [{
        "role":"user",
        "content": "Tell me what I should wear today using the information baout the weather."
    }]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    messages.append(response_message.to_dict())