# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tools module for the truck sharing service agent."""

import logging
import uuid
import json
from datetime import datetime, timedelta

# Import the agent instances - will be set later to avoid circular imports
firestore_agent_instance = None
weather_agent_instance = None

logger = logging.getLogger(__name__)


def send_call_companion_link(phone_number: str) -> str:
    """
    Sends a link to the user's phone number to start a video session for cargo viewing.

    Args:
        phone_number (str): The phone number to send the link to.

    Returns:
        dict: A dictionary with the status and message.

    Example:
        >>> send_call_companion_link(phone_number='+12065550123')
        {'status': 'success', 'message': 'Video link sent to +12065550123'}
    """

    logger.info("Sending video link to %s", phone_number)

    return {"status": "success", "message": f"Video link sent to {phone_number}"}


async def interact_with_firestore(query: str) -> str:
    """
    Interacts with the Firestore database via the FirestoreAgent.

    This function allows the truck sharing agent to store and retrieve customer data,
    bookings, vehicles, and other information from the Firestore database.

    Args:
        query (str): The query or command to send to the FirestoreAgent.
            Format: operation:collection:document_id[:data]
            
            Operations:
            - read: Read a document (read:collection_name:document_id)
            - write: Write a document (write:collection_name:document_id:json_data)
            - update: Update a document (update:collection_name:document_id:json_data)
            - delete: Delete a document (delete:collection_name:document_id)
            - query: Query a collection (query:collection_name:json_query_params)
            
            Examples:
            - read:users:user123
            - write:bookings:booking123:{"customerId":"123","pickupAddress":"123 Main St"}
            - update:bookings:booking456:{"status":"confirmed"}
            - delete:bookings:booking789
            - query:vehicles:{"filters":[{"field":"type","op":"==","value":"pickup"}]}

    Returns:
        str: The JSON result from the FirestoreAgent.

    Example:
        >>> await interact_with_firestore(query="read:users:user123")
        '{"success": true, "data": {"name": "Alex Johnson", "email": "alex@example.com"}, "id": "user123"}'
    """
    if not query:
        return json.dumps({"error": "Empty query provided"})
    
    logger.info("Interacting with Firestore with query: %s", query)
    
    if not firestore_agent_instance:
        return json.dumps({"error": "Firestore agent not initialized"})
    
    try:
        # Process the query through the Firestore agent
        result = await firestore_agent_instance.process_query(query)
        
        # Parse the result to make it more user-friendly
        try:
            result_dict = json.loads(result)
            
            # For bookings collection, add some customer-friendly details
            if "documents" in result_dict and query.startswith("query:bookings"):
                for doc in result_dict.get("documents", []):
                    # Format dates in a more readable way
                    if "pickupDateTime" in doc:
                        try:
                            pickup_date = doc["pickupDateTime"].split("T")[0]
                            pickup_time = doc["pickupDateTime"].split("T")[1].split("+")[0]
                            pickup_time = pickup_time.split(".")[0]  # Remove milliseconds if present
                            doc["formatted_pickup"] = f"{pickup_date} at {pickup_time}"
                        except (IndexError, AttributeError):
                            doc["formatted_pickup"] = doc["pickupDateTime"]
                    
                    # Add status description
                    if "status" in doc:
                        status_map = {
                            "pending": "Awaiting confirmation from truck owner",
                            "confirmed": "Booking confirmed, ready for pickup",
                            "in-progress": "Pickup in progress",
                            "completed": "Transportation completed",
                            "cancelled": "Booking cancelled", 
                            "declined": "Booking declined by truck owner"
                        }
                        doc["status_description"] = status_map.get(doc["status"], doc["status"])
                        
            # For vehicles collection, add some customer-friendly details
            if "documents" in result_dict and query.startswith("query:vehicles"):
                for doc in result_dict.get("documents", []):
                    # Add vehicle type description
                    if "type" in doc:
                        type_map = {
                            "pickup": "Standard Pickup Truck",
                            "van": "Moving Van",
                            "box truck": "Box Truck (Larger Cargo)",
                            "flatbed": "Flatbed Truck (Open Cargo Area)",
                            "other": "Specialty Vehicle"
                        }
                        doc["type_description"] = type_map.get(doc["type"], doc["type"])
                    
                    # Format price information clearly
                    if "hourlyRate" in doc:
                        doc["price_display"] = f"${doc['hourlyRate']:.2f}/hour"
                        
                    if "offerAssistance" in doc and doc["offerAssistance"] and "assistanceRate" in doc:
                        doc["assistance_display"] = f"Loading/unloading help available: ${doc['assistanceRate']:.2f}/hour"
            
            # Reserialize with the enhancements
            result = json.dumps(result_dict)
            
        except json.JSONDecodeError:
            # If we can't parse the result, just return it as is
            pass
        
        return result
    except Exception as e:
        logger.error(f"Error in interact_with_firestore: {e}")
        return json.dumps({"error": str(e)})


async def get_weather(location: str, days: int = 3) -> str:
    """
    Get weather forecast for a location using the Weather Agent.
    
    This function allows the truck sharing agent to provide weather information
    to customers who may be planning moves or deliveries that could be affected
    by weather conditions.
    
    Args:
        location (str): The city or location to get the weather forecast for
        days (int, optional): Number of days to forecast. Defaults to 3.
        
    Returns:
        str: JSON string containing the weather forecast data
        
    Example:
        >>> await get_weather(location="Chicago")
        '{"location": {"name": "Chicago", "country": "USA"}, "current": {"temp_c": 18, "condition": "Partly Cloudy", ...}, "forecast": {...}}'
    """
    if not weather_agent_instance:
        return json.dumps({"error": "Weather agent not initialized"})
    
    logger.info(f"Getting weather forecast for {location} for {days} days")
    
    try:
        # Call the weather agent's get_weather_forecast function
        result = weather_agent_instance.tools[0](location=location, days=days)
        
        # Format the response for better readability in the customer context
        try:
            weather_data = json.loads(result)
            
            # Add customer-friendly messaging
            if "error" not in weather_data:
                current = weather_data.get("current", {})
                condition = current.get("condition", "")
                temp = current.get("temp_c")
                
                if condition and temp is not None:
                    weather_data["customer_message"] = f"Currently {condition} and {temp}°C in {weather_data.get('location', {}).get('name', location)}"
                    
                    # Add moving/transportation recommendations based on weather
                    condition_lower = condition.lower()
                    if any(term in condition_lower for term in ["rain", "shower", "thunder", "snow", "storm"]):
                        weather_data["moving_tip"] = "Weather conditions might make loading/unloading difficult. Consider rescheduling if your items are sensitive to moisture or if safety is a concern."
                    elif any(term in condition_lower for term in ["sunny", "clear", "fair"]):
                        weather_data["moving_tip"] = "Excellent weather for moving! Just remember to stay hydrated if it's warm."
                    elif "wind" in condition_lower:
                        weather_data["moving_tip"] = "Windy conditions could make handling large items difficult. Take extra precautions with light, large objects."
                    elif any(term in condition_lower for term in ["cloud", "overcast", "fog"]):
                        weather_data["moving_tip"] = "Decent conditions for moving, but reduced visibility in fog could affect transportation safety."
                    else:
                        # Generic tip if condition doesn't match known patterns
                        weather_data["moving_tip"] = "Check local conditions before finalizing your moving plans."
            
            # Re-serialize with the customer-friendly enhancements
            result = json.dumps(weather_data)
            
        except json.JSONDecodeError:
            # If we can't parse the result, just return it as is
            pass
        
        return result
    except Exception as e:
        logger.error(f"Error in get_weather: {e}")
        return json.dumps({"error": str(e)})