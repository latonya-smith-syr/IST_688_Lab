import requests
import streamlit as st
from openai import OpenAI
import json


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

client = st.session_state.client

messages = [{
    "role": "user",
    "content": "Would you like to know the weather for today?"
}]

response = client.chat.completions.create(
    model=model,
    messages = messages,
    tools = tools,
    tool_choice="auto"
)

response_message = response.choices[0].messgae
messages.append(response_message.to_dict())

tool_calls = response_message.tool_calls
if tool_calls:
    tool_call_id = tool_calls[0].id
    tool_function_name = tool_calls[0].function.name
    tool_query_string = json.loads(tool_calls[0].function.arguments)['query']
else:
    print(response_message.content)


location = st.text_input("Input City, State")


if st.button("Get Weather", type="primary"):

    user_text = f"What should I wear today? Location: {location}" if location else "What should I wear today?"
    messages = ({"role": "user", "content": user_text})
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": get_current_weather,
        "content": location
    })

    model_response_with_function_call = client.chat.completions.create(
        model = model,
        messages=messages,
    )
    print(f"Result in database: {model_response_with_function_call.choices[0].message_content}")
else:
    print(f"Error: function {get_current_weather} does not exist")

    #response_message = response.choices[0].message.content
    #messages.append(response_message.to_dict())

