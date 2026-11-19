from agents import Agent, function_tool, Runner
import asyncio, os, time
import requests
import streamlit as st
from openai import OpenAI
import json

st.title("What To Wear Bot")

model = "gpt-5-mini"

os.environ["OPENAI_API_KEY"] = st.secrets["OPEN_API_KEY"]

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
@function_tool
def get_weather(location: str = "Syracuse, NY") -> dict:
    """Write a description of what this tool returns
    and what kind of locations it accepts."""
    return get_current_weather(location)

weather_agent = Agent(
    name="Weather agent",
    instructions= "Summarize today's weather for a given location. Facts only.",
    tools = [get_weather],
    model = model
)

stylist_agent = Agent(
    name = "Stylist agent",
    instructions="Recommend clothing for women and men for this weather."
)

activity_agent = Agent(
    name = "Activity agent",
    instructions= "Suggest activities that can be done in this weather"
)

manager_agent = Agent(
    name= "Manager",
    instructions= "Get the weather, then ask the stylist what to wear and combine both into one answer.",
    tools= [
        weather_agent.as_tool(
            tool_name="weather_report",
            tool_description="Summarize today's weather"
        ),
        stylist_agent.as_tool(
            tool_name="clothing_advice",
            tool_description="Recommend clothing for a forecast."
        ),
        activity_agent.as_tool(
            tool_name = "activity_recommendations",
            tool_description = "recommend t least 3 activities that I can comfortably do outdoors in the clothes that were recommended."
        ),
        ],
        model=model,
)

all_in_one_agent = Agent(
    name = "Emperor",
    instructions= "What should I wear today in this location? Give suggestions for outdoor activities that are appropriate to the weather.",
    tools = [get_weather],
    model = model
    
)
@st.cache_resource
def get_event_loop():
    return asyncio.new_event_loop()

def run(agent, prompt):
    start = time.perf_counter()
    result =get_event_loop().run_until_complete(Runner.run(agent, prompt))
    return result, time.perf_counter() - start

client = st.session_state.client

location = st.text_input("Input City, State")

agent_num = st.radio(
    "How many agents?",
    ["single_agent", "multiple_agent"],
    captions=[
        "One Agent",
        "Multiple Agents"
    ]
)

if st.button("Get Weather and Advice", type="primary"):
    if agent_num == "multiple_agent":
        user_text = f"What should I wear today? Location: {location}. Give suggestions for outdoor activities that are appropriate to the weather."
        result, seconds = run(manager_agent, user_text)
        message = st.chat_message("assistant")
        message.write(result.final_output)

        usage = result.context_wrapper.usage
        with st.expander("Behind the scenes"):
            st.write(f"Model requests: {usage.requests} · Tokens: {usage.total_tokens:,} · "
                f"Time: {seconds:.1f}s · Answered by: {result.last_agent.name}")
            for item in result.new_items:
                if item.type == "tool_call_item":
                    st.write(f"{item.agent.name} called {item.raw_item.name}: "
                        f"{item.raw_item.arguments}")
                elif item.type == "tool_call_output_item":
                    st.write(f"result: {str(item.output)[:300]}")
                elif item.type == "handoff_output_item":
                    st.write(f"handoff: {item.source_agent.name} -> {item.target_agent.name}")
    elif agent_num == "single_agent":
        user_text = f"What should I wear today? Location: {location}. Give suggestions for outdoor activities that are appropriate to the weather."
        result, seconds = run(all_in_one_agent, user_text)
        message = st.chat_message("assistant")
        message.write(result.final_output)
        usage = result.context_wrapper.usage
        with st.expander("Behind the scenes"):
            st.write(f"Model requests: {usage.requests} · Tokens: {usage.total_tokens:,} · "
                    f"Time: {seconds:.1f}s · Answered by: {result.last_agent.name}")
            for item in result.new_items:
                if item.type == "tool_call_item":
                    st.write(f"{item.agent.name} called {item.raw_item.name}: "
                        f"{item.raw_item.arguments}")
                elif item.type == "tool_call_output_item":
                    st.write(f"result: {str(item.output)[:300]}")
                elif item.type == "handoff_output_item":
                    st.write(f"handoff: {item.source_agent.name} -> {item.target_agent.name}")        



#Run it with a city and answer these in comments in your code file:
#a. Which tools did the manager call, and in what order? 
# The manager called weather_report first and then the clothing_advice and lastly, activity_recommendations

#b. What did the manager send to the stylist: the full forecast from the tool, or a summary? Who wrote that text?
#The manager sent the weather report to the stylist including all the information defined in the tool.

#c. “Model requests” is higher than the number of tool calls you see. Where did the other model calls happen?
#Each .as_tool() agent is a full agent run of its on. That is 3. Then weather agent makes at least 2 model calls, one to
#decide to call get_weather and one to write the summary, so that is 2 more. The stylist and activity agents each make atleast one so that is an 
#additional 2. The final call is to read all 3 results and write the final answer which is 1 more.
#This makes 8 calls.

