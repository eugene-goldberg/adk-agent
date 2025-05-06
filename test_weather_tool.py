"""
A simple test script for the Weather Agent's tools.
"""

import json
from weather_agent.tools.weather_api import get_weather_forecast

def test_weather_tool():
    """Test the weather tool with various locations."""
    print("Testing Weather API Tool...\n")
    
    # Test locations
    locations = ["tokyo", "london", "new york", "paris", "berlin"]
    
    for location in locations:
        print(f"Getting weather forecast for {location.title()}:")
        forecast_json = get_weather_forecast(location)
        forecast = json.loads(forecast_json)
        
        # Print current weather
        current = forecast.get("current", {})
        print(f"Current Weather: {current.get('temp_c')}°C, {current.get('condition')}")
        print(f"Humidity: {current.get('humidity')}%, Wind: {current.get('wind_kph')} km/h")
        
        # Print forecast for the first day
        days = forecast.get("forecast", {}).get("days", [])
        if days:
            day = days[0]
            print(f"Today's Forecast: {day.get('temp_min_c')}°C to {day.get('temp_max_c')}°C, {day.get('condition')}")
            print(f"Chance of Rain: {day.get('chance_of_rain')}%")
        
        print("\n" + "-" * 80 + "\n")
    
    # Test an invalid location
    print("Testing invalid location:")
    forecast_json = get_weather_forecast("invalidcity")
    forecast = json.loads(forecast_json)
    print(json.dumps(forecast, indent=2))

if __name__ == "__main__":
    test_weather_tool()