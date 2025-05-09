#!/usr/bin/env python3
"""
Test script for the Weather Agent integration with Customer Service Agent.
"""

import os
import asyncio
import json
from dotenv import load_dotenv

from customer_service.tools.tools import get_weather
from weather_agent.agent import weather_agent
from customer_service.tools import tools

async def test_weather_integration():
    """Test the Weather Agent integration with Customer Service Agent."""
    print("Testing Weather Agent Integration")
    print("-" * 50)
    
    # Set the weather agent instance
    tools.weather_agent_instance = weather_agent
    
    # Check if OpenWeatherMap API key is available
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    print(f"OpenWeatherMap API Key available: {bool(api_key)}")
    print("API Key set to:", "*" * len(api_key) if api_key else "None")
    
    # Test locations
    locations = ["New York", "Tokyo", "London", "Sydney"]
    
    # First try to test with the integrated agent function
    for location in locations:
        print(f"\nTesting weather for {location}:")
        result = await get_weather(location=location, days=3)
        
        # Parse the result
        try:
            weather_data = json.loads(result)
            if "error" in weather_data:
                print(f"Error: {weather_data['error']}")
                print("Trying fallback to direct weather API call...")
                # Try direct call to weather API function
                from weather_agent.tools.weather_api import get_weather_forecast
                result = get_weather_forecast(location=location, days=3)
                weather_data = json.loads(result)
                print("Using mock data from direct API call.")
            
            if "error" in weather_data:
                print(f"Error from direct call: {weather_data['error']}")
                continue
                
            # Print basic information
            location_info = weather_data.get("location", {})
            current = weather_data.get("current", {})
            forecast = weather_data.get("forecast", {}).get("days", [])
            
            print(f"Location: {location_info.get('name')}, {location_info.get('country')}")
            print(f"Current: {current.get('condition')}, {current.get('temp_c')}°C")
            print(f"Humidity: {current.get('humidity')}%, Wind: {current.get('wind_kph')} kph")
            
            if "customer_message" in weather_data:
                print(f"Customer message: {weather_data['customer_message']}")
                
            if "gardening_tip" in weather_data:
                print(f"Gardening tip: {weather_data['gardening_tip']}")
            
            # Print forecast
            print("\nForecast:")
            for day in forecast:
                print(f"  {day.get('date')}: {day.get('condition')}, {day.get('temp_min_c')}°C to {day.get('temp_max_c')}°C, Rain chance: {day.get('chance_of_rain')}%")
                
        except json.JSONDecodeError:
            print(f"Error parsing result: {result}")
    
    print("\nWeather Agent Integration test completed!")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the test
    asyncio.run(test_weather_integration())