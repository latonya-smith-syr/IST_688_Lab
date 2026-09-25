import requests
import streamlit as st
from openai import OpenAI


st.title("What To Wear Bot")

model = "gpt-4o-mini"

if 'client' not in st.session_state:
    api_key = st.secrets["OPEN_API_KEY"]
    st.session_state.client= OpenAI(api_key=api_key)

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

location = st.text_input("Input City, State")

client = st.session_state.client

if st.button("Get Weather", type="primary"):
    client = st.session_state.client

    user_text = f"What should I wear today? Location: {location}" if location else "What should I wear today?"
    messages = [{"role": "user", "content": user_text}]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    messages.append(response_message.to_dict())