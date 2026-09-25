import requests
import streamlit as st
from openai import OpenAI
import json


st.title("What To Wear Bot")

model = "gpt-4o-mini"

if 'client' not in st.session_state:
    api_key = st.secrets["OPEN_API_KEY"]
    st.session_state.client = OpenAI(api_key=api_key)

def get_current_weather(location):
    url = f'https://wttr.in/{location}?format=j1'
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        raise Exception(f"wttr.in error: status {response.status_code}")
    try:
        data = response.json()
    except ValueError:
        raise Exception(f"Could not find a location named {location}")
    current = data['current_condition'][0]

    return {
        'location': location,
        'temperature': float(current['temp_F']),
        'description': current['weatherDesc'][0]['value'],
        'FeelsLikeF': int(current['FeelsLikeF']),
        'visibility': float(current['visibility']),
        'humidity': int(current['humidity']),
        'uvIndex': int(current['uvIndex']),
        'windspeedMiles': float(current['windspeedMiles'])
    }

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                },
                "required": ["location"],
            },
        },
    }
]

client = st.session_state.client

location = st.text_input("Input City, State")

if st.button("Get Weather", type="primary"):

    effective_location = location if location else "Syracuse, NY"

    user_text = f"What should I wear today? Location: {effective_location}. Give suggestions for outdoor activities that are appropriate to the weather."
    messages = [{"role": "user", "content": user_text}]


    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    response_message = response.choices[0].message
    messages.append(response_message.to_dict())

    tool_calls = response_message.tool_calls

    if tool_calls:
        tool_call_id = tool_calls[0].id
        tool_function_name = tool_calls[0].function.name
        tool_location = json.loads(tool_calls[0].function.arguments).get('location') or "Syracuse, NY"

        if tool_function_name == "get_current_weather":
            try:
                weather_result = get_current_weather(tool_location)
            except Exception as e:
                weather_result = {"error": str(e)}


            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": tool_function_name,
                "content": json.dumps(weather_result)
            })

            final_response = client.chat.completions.create(
                model=model,
                messages=messages
            )

            st.write(final_response.choices[0].message.content)
        else:
            st.write(f"Error: function {tool_function_name} is not recognized")
    else:
        st.write(response_message.content)