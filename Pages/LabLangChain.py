import requests
import os
import streamlit as st
from openai import OpenAI
import json
import langchain
import langchain_openai
from langchain.agents import create_agent

os.environ["OPENAI_API_KEY"] = st.secrets["OPEN_API_KEY"]


def get_current_weather(location):
    """
    This function takes a location in the form of a city, state, 
    makes a request to the url and receives teh following information about the weather
    in that location. They are the temperature, description,
    the temperature it feels like, the visibility, the humidity, the uvIndex and teh windspeed in miles.
    """
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

location = st.text_input("Input City, State")
#st.button("Get Weather", type="primary")

agent = create_agent(
    model= "openai:gpt-5-mini", 
    tools=[get_current_weather], 
    system_prompt= "Give suggestions for outdoor activities that are appropriate to the weather",
    )
    # inside your button block:
if st.button("Get Weather", type="primary"):
    result = agent.invoke(
        {"messages": [{"role": "user", "content": f"What should I wear in{location}?"}]}
)

    message = st.chat_message("assistant")
    message.write(result["messages"][3].content)

    with st.expander("Behind the scenes"):
        for message in result["messages"]:
            st.write(f"**{message.type}**")
            st.write(message.content)
            if message.type == "ai" and message.tool_calls:
                st.write(message.tool_calls)

    #

