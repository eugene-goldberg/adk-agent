"""
Weather API Tool for the Weather Agent.

This module provides a tool to get weather forecasts for locations
using the OpenWeatherMap API.
"""

import json
import os
import requests
from datetime import datetime
from typing import Optional

# OpenWeatherMap API URL and endpoints
BASE_URL = "https://api.openweathermap.org/data/2.5"
CURRENT_WEATHER_ENDPOINT = "/weather"
FORECAST_ENDPOINT = "/forecast"
GEO_ENDPOINT = "http://api.openweathermap.org/geo/1.0/direct"

# Environment variable for API key
API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

def get_weather_forecast(location: str, days: int = 3) -> str:
    """
    Get a weather forecast for a specific location using OpenWeatherMap API.
    
    Args:
        location (str): The city name to get weather for
        days (int, optional): Number of days to forecast. Defaults to 3.
    
    Returns:
        str: JSON string containing the weather forecast data
    """
    # Check if API key is available
    if not API_KEY:
        return json.dumps({
            "error": "OpenWeatherMap API key not found. Please set the OPENWEATHERMAP_API_KEY environment variable."
        })
    
    try:
        # First, get the coordinates for the location
        geo_coordinates = get_coordinates(location)
        if not geo_coordinates:
            return json.dumps({
                "error": f"Location '{location}' not found. Please check the spelling or try a different location."
            })
        
        lat, lon, country, city_name = geo_coordinates
        
        # Get current weather
        current_weather = get_current_weather(lat, lon)
        if not current_weather:
            return json.dumps({
                "error": f"Unable to get current weather data for '{location}'."
            })
        
        # Get forecast
        forecast_days = get_forecast(lat, lon, days)
        if not forecast_days:
            return json.dumps({
                "error": f"Unable to get forecast data for '{location}'."
            })
        
        # Combine data into our expected format
        result = {
            "location": {
                "name": city_name,
                "country": country,
                "coordinates": {"lat": lat, "lon": lon}
            },
            "current": current_weather,
            "forecast": {
                "days": forecast_days
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"An error occurred: {str(e)}"
        })

def get_coordinates(location: str) -> Optional[tuple]:
    """
    Get the latitude and longitude for a location using OpenWeatherMap Geocoding API.
    
    Args:
        location (str): City name to look up
        
    Returns:
        Optional[tuple]: Tuple of (lat, lon, country, city_name) or None if not found
    """
    params = {
        "q": location,
        "limit": 1,
        "appid": API_KEY
    }
    
    response = requests.get(GEO_ENDPOINT, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data and len(data) > 0:
            location_data = data[0]
            return (
                location_data.get("lat"),
                location_data.get("lon"),
                location_data.get("country"),
                location_data.get("name")
            )
    
    return None

def get_current_weather(lat: float, lon: float) -> Optional[dict]:
    """
    Get current weather data for the specified coordinates.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        
    Returns:
        Optional[dict]: Dictionary with current weather or None on failure
    """
    params = {
        "lat": lat,
        "lon": lon,
        "units": "metric",  # Use Celsius
        "appid": API_KEY
    }
    
    response = requests.get(f"{BASE_URL}{CURRENT_WEATHER_ENDPOINT}", params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Convert OpenWeatherMap format to our expected format
        weather = {
            "temp_c": data.get("main", {}).get("temp"),
            "condition": data.get("weather", [{}])[0].get("main"),
            "description": data.get("weather", [{}])[0].get("description"),
            "humidity": data.get("main", {}).get("humidity"),
            "wind_kph": convert_ms_to_kph(data.get("wind", {}).get("speed", 0)),
            "pressure": data.get("main", {}).get("pressure"),
            "feels_like": data.get("main", {}).get("feels_like")
        }
        
        return weather
    
    return None

def get_forecast(lat: float, lon: float, days: int) -> Optional[list]:
    """
    Get weather forecast for the specified coordinates.
    
    Args:
        lat (float): Latitude
        lon (float): Longitude
        days (int): Number of days to forecast
        
    Returns:
        Optional[list]: List of daily forecasts or None on failure
    """
    params = {
        "lat": lat,
        "lon": lon,
        "units": "metric",  # Use Celsius
        "appid": API_KEY
    }
    
    response = requests.get(f"{BASE_URL}{FORECAST_ENDPOINT}", params=params)
    
    if response.status_code == 200:
        data = response.json()
        forecast_items = data.get("list", [])
        
        # OpenWeatherMap's free tier provides 5-day forecast in 3-hour steps
        # We'll process this into daily forecasts
        daily_forecasts = process_forecast(forecast_items, days)
        
        return daily_forecasts
    
    return None

def process_forecast(forecast_items: list, days: int) -> list:
    """
    Process OpenWeatherMap forecast items into daily forecasts.
    
    Args:
        forecast_items (list): List of forecast time points
        days (int): Number of days to include
        
    Returns:
        list: Processed daily forecasts
    """
    # Group forecasts by day
    forecasts_by_day = {}
    
    for item in forecast_items:
        timestamp = item.get("dt")
        date = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        
        if date not in forecasts_by_day:
            forecasts_by_day[date] = []
            
        forecasts_by_day[date].append(item)
    
    # Process each day's forecast
    result = []
    days_processed = 0
    
    for date, items in sorted(forecasts_by_day.items()):
        if days_processed >= days:
            break
            
        temps = [item.get("main", {}).get("temp") for item in items]
        min_temp = min(temps) if temps else None
        max_temp = max(temps) if temps else None
        
        # Get the most common weather condition for the day
        conditions = [item.get("weather", [{}])[0].get("main") for item in items]
        condition = max(set(conditions), key=conditions.count) if conditions else None
        
        # Calculate chance of rain (percentage of periods with rain)
        rain_periods = sum(1 for item in items if "rain" in item)
        chance_of_rain = int((rain_periods / len(items)) * 100) if items else 0
        
        daily_forecast = {
            "date": date,
            "temp_min_c": min_temp,
            "temp_max_c": max_temp,
            "condition": condition,
            "chance_of_rain": chance_of_rain,
            # We don't have sunrise/sunset in the forecast data
            "sunrise": None,
            "sunset": None
        }
        
        result.append(daily_forecast)
        days_processed += 1
    
    return result

def convert_ms_to_kph(speed_ms: float) -> float:
    """
    Convert wind speed from meters per second to kilometers per hour.
    
    Args:
        speed_ms (float): Speed in m/s
        
    Returns:
        float: Speed in km/h
    """
    return round(speed_ms * 3.6, 1)  # 1 m/s = 3.6 km/h