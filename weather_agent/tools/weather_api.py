"""
Weather API Tool for the Weather Agent.

This module provides a tool to get weather forecasts for locations.
In a real implementation, this would call an actual weather API.
"""

import json
import random
from datetime import datetime, timedelta

# Mock weather data for demonstration purposes
WEATHER_CONDITIONS = ["Sunny", "Partly Cloudy", "Cloudy", "Rainy", "Thunderstorms", "Snowy", "Windy"]
CITIES = {
    "new york": {"country": "USA", "temp_range": (0, 35)},
    "london": {"country": "UK", "temp_range": (-5, 30)},
    "tokyo": {"country": "Japan", "temp_range": (0, 35)},
    "sydney": {"country": "Australia", "temp_range": (10, 40)},
    "paris": {"country": "France", "temp_range": (-5, 35)},
    "berlin": {"country": "Germany", "temp_range": (-10, 35)},
    "cairo": {"country": "Egypt", "temp_range": (15, 45)},
    "rio de janeiro": {"country": "Brazil", "temp_range": (20, 40)},
    "moscow": {"country": "Russia", "temp_range": (-30, 30)},
    "beijing": {"country": "China", "temp_range": (-15, 40)},
}

def get_weather_forecast(location: str, days: int = 3) -> str:
    """
    Get a weather forecast for a specific location.
    
    Args:
        location (str): The city name to get weather for
        days (int, optional): Number of days to forecast. Defaults to 3.
    
    Returns:
        str: JSON string containing the weather forecast data
    """
    location = location.lower()
    
    # Check if the location is in our mock database
    if location not in CITIES:
        return json.dumps({
            "error": f"Location '{location}' not found. Try one of: {', '.join(CITIES.keys())}"
        })
    
    city_info = CITIES[location]
    
    # Generate a mock forecast
    forecast = {
        "location": {
            "name": location.title(),
            "country": city_info["country"],
        },
        "current": {
            "temp_c": random.randint(city_info["temp_range"][0], city_info["temp_range"][1]),
            "condition": random.choice(WEATHER_CONDITIONS),
            "humidity": random.randint(30, 90),
            "wind_kph": random.randint(0, 50),
        },
        "forecast": {
            "days": []
        }
    }
    
    # Generate forecast for the requested number of days
    today = datetime.now()
    
    for i in range(days):
        forecast_date = today + timedelta(days=i)
        min_temp = random.randint(city_info["temp_range"][0], 
                                 city_info["temp_range"][0] + (city_info["temp_range"][1] - city_info["temp_range"][0]) // 2)
        max_temp = random.randint(min_temp, city_info["temp_range"][1])
        
        daily_forecast = {
            "date": forecast_date.strftime("%Y-%m-%d"),
            "temp_min_c": min_temp,
            "temp_max_c": max_temp,
            "condition": random.choice(WEATHER_CONDITIONS),
            "chance_of_rain": random.randint(0, 100),
            "sunrise": "06:30 AM" if i == 0 else None,  # Only provide sunrise/sunset for today
            "sunset": "08:15 PM" if i == 0 else None
        }
        
        forecast["forecast"]["days"].append(daily_forecast)
    
    return json.dumps(forecast, indent=2)