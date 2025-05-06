"""
Weather Agent implementation using Google's Agent Development Kit (ADK).
"""

from google.adk.agents import Agent

from weather_agent.prompt import ROOT_AGENT_INSTRUCTION
from weather_agent.tools import get_weather_forecast

# Define the weather agent
weather_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="A weather assistant that provides forecasts for locations",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[get_weather_forecast],
)