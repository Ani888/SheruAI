import os
import requests
import streamlit as st

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import create_react_agent, AgentExecutor
from langsmith import Client

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")


# --------------------------------------------------
# Tools
# --------------------------------------------------

search_tool = TavilySearchResults(max_results=2)


@tool
def get_weather_data(city: str) -> str:
    """
    Fetch current weather information for a city.
    """

    url = (
        f"https://api.weatherstack.com/current?"
        f"access_key={WEATHERSTACK_API_KEY}&query={city}"
    )

    response = requests.get(url)
    data = response.json()

    if "current" not in data:
        return f"Could not fetch weather data for {city}"

    return (
        f"City: {city}\n"
        f"Temperature: {data['current']['temperature']}°C\n"
        f"Weather: {data['current']['weather_descriptions'][0]}\n"
        f"Humidity: {data['current']['humidity']}%"
    )


# --------------------------------------------------
# LLM
# --------------------------------------------------

llm_1 = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=GROQ_API_KEY
)


# --------------------------------------------------
# Prompt
# --------------------------------------------------

client = Client()

prompt = client.pull_prompt(
    "hwchase17/react",
    dangerously_pull_public_prompt=True
)


# --------------------------------------------------
# Agent
# --------------------------------------------------

tools = [
    search_tool,
    get_weather_data
]

agent = create_react_agent(
    llm=llm_1,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)


# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------

st.set_page_config(
    page_title="My AI Agent",
    page_icon="🤖"
)

st.title("🤖 SheruAI")
st.write("Ask me about weather, current information, and more.")


# --------------------------------------------------
# Chat history
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# User input
# --------------------------------------------------

user_input = st.chat_input(
    "Ask something..."
)


if user_input:

    # Show user message
    st.chat_message("user").markdown(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })


    # Run agent
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                response = agent_executor.invoke({
                    "input": user_input
                })

                answer = response["output"]

            except Exception as e:

                answer = f"Error: {str(e)}"


        st.markdown(answer)


    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })