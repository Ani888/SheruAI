import os
import certifi
import requests
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults  ## search tool  used for internet search
from langchain import hub
from langsmith import Client
from langchain.tools import tool

from langchain.agents import create_react_agent, AgentExecutor   ## react ----> Reasoning and action == ReAct this is langchain agent to create our agent

load_dotenv()

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
WEATHERSTACK_API_KEY=os.getenv("WEATHERSTACK_API_KEY")

search_tool= TavilySearchResults(max_results=2)

@tool         ##if i want to use custom function as tool then i have to use decorator (@) now it become custom tool
def get_weather_data(city:str) -> str :
        """
        Fetch current weather information for a city.
        """

        url=(
                f"https://api.weatherstack.com/current?"
                f"access_key={WEATHERSTACK_API_KEY}&query={city}"
        )
        print(url)

        response = requests.get(url)

        data = response.json()

        if "current" not in data:
                return f"Could not fetch weather data for {city}"
        
        print(data['current'])

        return (
                f"City:{city}\n"
                f"Temperature: {data['current']['temperature']}°C\n"  ##option+shift+8 for degree sign
                f"Weather: {data['current']['weather_descriptions'][0]}\n"
                f"Humidity: {data['current']['humidity']}%"
        )

result = get_weather_data("delhi")
result = search_tool.invoke("What is the current score of India in cricket today match")

llm_1=ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=GROQ_API_KEY
)

response= llm_1.invoke("what is your last trained year")

client = Client()
prompt = client.pull_prompt("hwchase17/react", dangerously_pull_public_prompt=True)


tools=[search_tool, get_weather_data]

agent = create_react_agent(
        llm=llm_1,
        tools=tools,
        prompt=prompt
)


agent_executor= AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True ,   ## to see the log of plans and all (to able to see execution process)
        handle_parsing_errors=True    
)


response = agent_executor.invoke({
        "input": (
                " find its current weather of delhi."
        )
})

print(response["output"])