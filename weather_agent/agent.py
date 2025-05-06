"""
Weather Agent implementation using Google's Agent Development Kit (ADK).
"""

from google.adk.agents import Agent

from weather_agent.prompt import ROOT_AGENT_INSTRUCTION
from weather_agent.tools import get_weather_forecast

# Define the weather agent (named root_agent for ADK CLI compatibility)
root_agent = Agent(
    name="weather_agent",
    model="gemini-2.0-flash",
    description="A weather assistant that provides forecasts for locations",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[get_weather_forecast],
)

# Also keep weather_agent reference for backward compatibility
weather_agent = root_agent