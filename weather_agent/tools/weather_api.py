"""
Weather API Tool for the Weather Agent.

This module provides a tool to get weather forecasts for locations
using the wttr.in API, which doesn't require authentication.
"""

import json
import requests
from datetime import datetime, timedelta
from urllib.parse import quote

def get_weather_forecast(location: str, days: int = 3) -> str:
    """
    Get a weather forecast for a specific location using wttr.in API.
    
    Args:
        location (str): The city name to get weather for
        days (int, optional): Number of days to forecast. Defaults to 3.
    
    Returns:
        str: JSON string containing the weather forecast data
    """
    try:
        # URL encode the location to handle spaces and special characters
        encoded_location = quote(location)
        
        # Fetch data from wttr.in API (JSON format)
        url = f"https://wttr.in/{encoded_location}?format=j1"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return json.dumps({
                "error": f"Failed to get weather data: HTTP {response.status_code}"
            })
            
        # Check if response is valid JSON - some locations return HTML instead of JSON
        try:
            if response.text.strip() and response.text[0] != '{':
                # Not valid JSON, try a different approach
                return json.dumps({
                    "error": f"Location '{location}' not found or returned invalid data. Try a more specific location name."
                })
            # Empty response check
            if not response.text.strip():
                return json.dumps({
                    "error": f"No data returned for location '{location}'. Try a different location."
                })
        except Exception:
            return json.dumps({
                "error": f"Invalid response for location '{location}'. Try a different location."
            })
        
        # Parse the wttr.in response
        wttr_data = response.json()
        
        # Extract current conditions
        current_condition = wttr_data.get("current_condition", [{}])[0]
        
        # Extract location information
        location_info = wttr_data.get("nearest_area", [{}])[0]
        country = location_info.get("country", [{}])[0].get("value", "")
        city = location_info.get("areaName", [{}])[0].get("value", location)
        
        # Build our response format
        result = {
            "location": {
                "name": city,
                "country": country,
                "coordinates": {
                    "lat": location_info.get("latitude", ""),
                    "lon": location_info.get("longitude", "")
                }
            },
            "current": {
                "temp_c": float(current_condition.get("temp_C", 0)),
                "condition": current_condition.get("weatherDesc", [{}])[0].get("value", ""),
                "humidity": int(current_condition.get("humidity", 0)),
                "wind_kph": float(current_condition.get("windspeedKmph", 0)),
                "feels_like": float(current_condition.get("FeelsLikeC", 0)),
                "pressure": int(current_condition.get("pressure", 0)),
                "uv_index": int(current_condition.get("uvIndex", 0))
            },
            "forecast": {
                "days": []
            }
        }
        
        # Process forecast data for requested number of days
        # wttr.in provides forecast in the "weather" array
        weather_forecast = wttr_data.get("weather", [])
        
        # Limit to requested days and if there's less data than requested, use what's available
        days_to_process = min(days, len(weather_forecast))
        
        for i in range(days_to_process):
            day_data = weather_forecast[i]
            date = day_data.get("date", "")
            
            # Find max and min temperatures
            hourly = day_data.get("hourly", [])
            if hourly:
                temps = [float(h.get("tempC", 0)) for h in hourly]
                min_temp = min(temps) if temps else None
                max_temp = max(temps) if temps else None
                
                # Get the most common weather condition for the day
                conditions = [h.get("weatherDesc", [{}])[0].get("value", "") for h in hourly]
                # Simple mode function to get most common condition
                if conditions:
                    condition = max(set(conditions), key=conditions.count)
                else:
                    condition = ""
                
                # Calculate chance of rain (maximum chance across the day)
                chance_of_rain = max([int(h.get("chanceofrain", 0)) for h in hourly])
                
                # Extract astronomy data for sunrise/sunset if available
                astronomy = day_data.get("astronomy", [{}])
                sunrise = astronomy[0].get("sunrise", "") if astronomy else None
                sunset = astronomy[0].get("sunset", "") if astronomy else None
                
                daily_forecast = {
                    "date": date,
                    "temp_min_c": min_temp,
                    "temp_max_c": max_temp,
                    "condition": condition,
                    "chance_of_rain": chance_of_rain,
                    "sunrise": sunrise,
                    "sunset": sunset
                }
                
                result["forecast"]["days"].append(daily_forecast)
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"An error occurred: {str(e)}"
        })