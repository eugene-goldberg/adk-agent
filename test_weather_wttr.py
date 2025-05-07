#!/usr/bin/env python3
"""
Test script for the Weather Agent using wttr.in API.
"""

import json
import asyncio

from weather_agent.tools.weather_api import get_weather_forecast
from customer_service.tools.tools import get_weather
from weather_agent.agent import weather_agent
from customer_service.tools import tools

async def test_weather_agent():
    """Test both direct API calls and through agent integration."""
    print("Testing Weather Agent with wttr.in API")
    print("-" * 50)
    
    # Set up the weather agent instance for the tools module
    tools.weather_agent_instance = weather_agent
    
    # Test locations
    locations = ["New York", "Tokyo", "London", "San Francisco"]
    
    # Test direct API calls
    print("\n1. Testing direct API calls:")
    for location in locations:
        print(f"\nWeather for {location}:")
        result = get_weather_forecast(location=location, days=3)
        weather_data = json.loads(result)
        
        if "error" in weather_data:
            print(f"  Error: {weather_data['error']}")
            continue
        
        # Print current weather
        current = weather_data.get("current", {})
        location_info = weather_data.get("location", {})
        print(f"  Location: {location_info.get('name')}, {location_info.get('country')}")
        print(f"  Current: {current.get('condition')}, {current.get('temp_c')}°C")
        print(f"  Humidity: {current.get('humidity')}%, Wind: {current.get('wind_kph')} kph")
        
        # Print first day of forecast
        forecast = weather_data.get("forecast", {}).get("days", [])
        if forecast:
            first_day = forecast[0]
            print(f"  Tomorrow: {first_day.get('condition')}, {first_day.get('temp_min_c')}°C to {first_day.get('temp_max_c')}°C")
    
    # Test through agent integration
    print("\n\n2. Testing through Customer Service agent integration:")
    for location in locations:
        print(f"\nWeather for {location} (via agent):")
        result = await get_weather(location=location, days=3)
        weather_data = json.loads(result)
        
        if "error" in weather_data:
            print(f"  Error: {weather_data['error']}")
            continue
        
        # Print customer-friendly message
        if "customer_message" in weather_data:
            print(f"  {weather_data['customer_message']}")
        
        # Print gardening tip
        if "gardening_tip" in weather_data:
            print(f"  Gardening Tip: {weather_data['gardening_tip']}")
        
        # Print forecast summary
        forecast = weather_data.get("forecast", {}).get("days", [])
        if forecast:
            print("\n  3-Day Forecast:")
            for day in forecast:
                print(f"    {day.get('date')}: {day.get('condition')}, {day.get('temp_min_c')}°C to {day.get('temp_max_c')}°C")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_weather_agent())