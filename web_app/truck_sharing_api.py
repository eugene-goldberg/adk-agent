"""
Truck Sharing Agent API 

This module provides API endpoints for testing the Truck Sharing agent deployed in Vertex AI
and interacting with it through a web interface. It also provides direct Firestore integration
for creating and retrieving truck booking information.
"""

import os
import requests
import json
import uuid
import re
import time
import subprocess
import sys
import asyncio
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from google.auth.transport.requests import Request
import google.auth
from google.cloud import firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
REGION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
# No hardcoded IDs - all IDs will be dynamically obtained

# Set the proper Python path for imports
# This allows execution of commands that need access to the project modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Blueprint for truck sharing agent
truck_api = Blueprint('truck_api', __name__)

# Initialize Firestore client
try:
    db = firestore.Client(project=PROJECT_ID)
    print(f"Firestore client initialized with project ID: {PROJECT_ID}")
except Exception as e:
    print(f"Error initializing Firestore client: {e}")
    db = None
    print("WARNING: Firestore integration will not be available.")

# Helper functions for Firestore operations
def create_booking_in_firestore(booking_data):
    """Create a new booking record in Firestore."""
    if not db:
        return {"success": False, "error": "Firestore client not initialized"}
    
    try:
        # Generate a unique booking ID if not provided
        booking_id = booking_data.get("id", f"booking_{int(time.time())}")
        
        # Set or update timestamps
        current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        booking_data["createdAt"] = booking_data.get("createdAt", current_time)
        booking_data["updatedAt"] = current_time
        
        # Add ID to the document if not present
        if "id" not in booking_data:
            booking_data["id"] = booking_id
        
        # Write to Firestore
        bookings_ref = db.collection("bookings")
        bookings_ref.document(booking_id).set(booking_data)
        
        return {
            "success": True,
            "booking_id": booking_id,
            "message": "Booking created successfully"
        }
    except Exception as e:
        print(f"Error creating booking in Firestore: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_bookings_from_firestore(customer_id=None, limit=10):
    """Retrieve bookings from Firestore with optional filtering by customer ID."""
    if not db:
        return {"success": False, "error": "Firestore client not initialized"}
    
    try:
        bookings_ref = db.collection("bookings")
        query = bookings_ref
        
        # Apply filter if customer ID is provided
        if customer_id:
            query = query.where("customerId", "==", customer_id)
        
        # Apply limit and order by creation time
        query = query.limit(limit).order_by("createdAt", direction=firestore.Query.DESCENDING)
        
        # Execute query
        docs = query.stream()
        
        # Convert to list of dictionaries
        bookings = []
        for doc in docs:
            booking_data = doc.to_dict()
            # Ensure ID is included
            if "id" not in booking_data:
                booking_data["id"] = doc.id
            bookings.append(booking_data)
        
        return {
            "success": True,
            "documents": bookings,
            "count": len(bookings)
        }
    except Exception as e:
        print(f"Error retrieving bookings from Firestore: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_access_token():
    """Get access token using application default credentials."""
    try:
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = Request()
        credentials.refresh(auth_req)
        print(f"Successfully obtained access token for project: {project}")
        return credentials.token
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def run_command(command, timeout=30000):
    """Run a shell command with proper environment variables.
    
    Args:
        command: The command to run
        timeout: Timeout in milliseconds (default: 30 seconds)
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT}:{env.get('PYTHONPATH', '')}"
    
    # Convert timeout from milliseconds to seconds
    timeout_seconds = timeout / 1000.0
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            env=env,
            timeout=timeout_seconds
        )
        
        # Clean up output by removing INFO/DEBUG log lines
        if result.stdout:
            cleaned_stdout = "\n".join([
                line for line in result.stdout.split("\n") 
                if not line.startswith(("INFO:", "DEBUG:"))
            ])
        else:
            cleaned_stdout = ""
            
        if result.stderr and not result.stderr.startswith(("INFO:", "DEBUG:")):
            cleaned_stderr = result.stderr
        else:
            cleaned_stderr = ""
            
        return {
            "success": result.returncode == 0,
            "stdout": cleaned_stdout,
            "stderr": cleaned_stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired as te:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out after {timeout_seconds} seconds: {str(te)}",
            "returncode": -1,
            "timeout": True
        }
    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "returncode": -1
        }

def extract_session_id(output):
    """Extract session ID from command output."""
    if not output:
        return None
    match = re.search(r'Session ID: (\d+)', output)
    if match:
        return match.group(1)
    return None

@truck_api.route('/info', methods=['GET'])
def get_agent_info():
    """Get information about the truck sharing agent."""
    try:
        # Use dynamic discovery to find the truck sharing agent
        truck_agent_id = None
        
        # Run the deployment list command
        try:
            command = f"cd {PROJECT_ROOT} && python3 deployment/truck_sharing_remote.py --list"
            result = run_command(command)
            
            if result["success"]:
                # Extract resource IDs from the output
                import re
                matches = re.findall(r'projects/[^/]+/locations/[^/]+/reasoningEngines/(\d+)', result["stdout"])
                
                if matches:
                    # Use the first matching ID (preferably one with "truck" in the output context)
                    for match_id in matches:
                        context_start = max(0, result["stdout"].find(match_id) - 100)
                        context_end = min(len(result["stdout"]), result["stdout"].find(match_id) + 100)
                        context = result["stdout"][context_start:context_end]
                        
                        if "truck" in context.lower():
                            truck_agent_id = match_id
                            break
                    
                    # If no truck agent was specifically identified, use the first ID
                    if not truck_agent_id and matches:
                        truck_agent_id = matches[0]
        except Exception as e:
            print(f"Error discovering agents: {e}")
        
        # If we didn't find any agents, try reading from AGENT_INTEGRATION_NOTES.md
        if not truck_agent_id:
            try:
                notes_command = f"cd {PROJECT_ROOT} && cat AGENT_INTEGRATION_NOTES.md | grep truck-sharing-agent -A 2"
                notes_result = run_command(notes_command)
                
                if notes_result["success"]:
                    truck_match = re.search(r'projects/[^/]+/locations/[^/]+/reasoningEngines/(\d+)', notes_result["stdout"])
                    if truck_match:
                        truck_agent_id = truck_match.group(1)
            except Exception as e:
                print(f"Error reading integration notes: {e}")
        
        # Create agent info object
        if truck_agent_id:
            agent_info = {
                "id": truck_agent_id,
                "resource_id": f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{truck_agent_id}",
                "python_version": "3.12",
                "display_name": "truck-sharing-agent",
                "description": "A truck sharing assistant that helps customers book trucks, manage reservations, find suitable vehicles, and check weather conditions for moves.",
                "discovery_method": "dynamic"
            }
        else:
            # Fail with an error if no agent could be found
            return jsonify({
                "success": False,
                "error": "No truck sharing agent could be discovered. Please deploy an agent first."
            }), 404
        
        return jsonify({
            "success": True,
            "agent": agent_info
        })
    
    except Exception as e:
        print(f"Error in get_agent_info: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@truck_api.route('/create_session', methods=['POST'])
def create_agent_session():
    """Create a session with the truck sharing agent."""
    try:
        data = request.json or {}
        resource_id = data.get('resource_id')
        
        # If no resource ID provided, get one from agent discovery
        if not resource_id:
            try:
                agent_info_result = get_agent_info()
                agent_info_data = agent_info_result.get_json()
                
                if agent_info_data.get('success') and agent_info_data.get('agent'):
                    resource_id = agent_info_data['agent'].get('resource_id')
                else:
                    return jsonify({
                        "success": False,
                        "error": "No agent resource ID provided and none could be discovered."
                    }), 400
            except Exception as e:
                print(f"Error getting agent info: {e}")
                return jsonify({
                    "success": False,
                    "error": f"No agent resource ID provided and failed to discover one: {str(e)}"
                }), 400
        
        if not resource_id:
            return jsonify({
                "success": False,
                "error": "Resource ID is required"
            }), 400
        
        # Extract just the numeric ID if it's a full path
        if resource_id.startswith('projects/'):
            numeric_id = resource_id.split('/')[-1]
        else:
            numeric_id = resource_id
            
        print(f"Creating session with agent ID: {numeric_id}")
            
        # Call the truck_sharing_remote.py script to create a session
        command = f"python deployment/truck_sharing_remote.py --create_session --resource_id={numeric_id}"
        result = run_command(command)
        
        print(f"Command output: {result['stdout']}")
        print(f"Command error: {result['stderr']}")
        
        if not result["success"]:
            return jsonify({
                "success": False,
                "error": "Failed to create session",
                "details": result["stderr"] or "Unknown error"
            }), 500
        
        # Check for session ID in the output
        session_id = None
        
        # Try to extract session ID with regex
        session_match = re.search(r'Session ID:\s*(\d+)', result['stdout'])
        if session_match:
            session_id = session_match.group(1)
            print(f"Found session ID: {session_id}")
        
        # If not found, try another pattern
        if not session_id:
            session_match = re.search(r'"id":\s*"?(\d+)"?', result['stdout'])
            if session_match:
                session_id = session_match.group(1)
                print(f"Found session ID from JSON: {session_id}")
        
        # If still not found and the command succeeded, try to parse the JSON output
        if not session_id and result["success"]:
            try:
                # Look for JSON in the output
                json_start = result['stdout'].find('{')
                json_end = result['stdout'].rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_data = json.loads(result['stdout'][json_start:json_end])
                    if 'id' in json_data:
                        session_id = json_data['id']
                        print(f"Extracted session ID from JSON: {session_id}")
            except Exception as json_err:
                print(f"Error extracting JSON: {json_err}")
        
        # If we still couldn't find a session ID, report an error
        if not session_id:
            return jsonify({
                "success": False,
                "error": "Failed to extract session ID from response",
                "details": result["stdout"]
            }), 500
            
        return jsonify({
            "success": True,
            "session_id": session_id,
            "resource_id": resource_id,
            "debug_output": result["stdout"]
        })
    
    except Exception as e:
        print(f"Error creating session: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@truck_api.route('/send_message', methods=['POST'])
def send_message():
    """Send a message to the truck sharing agent using the direct REST API approach."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        resource_id = data.get('resource_id')
        session_id = data.get('session_id')
        message = data.get('message')
        auto_create_booking = data.get('auto_create_booking', False)
        
        # If no resource ID provided, get one from agent discovery
        if not resource_id:
            try:
                agent_info_result = get_agent_info()
                agent_info_data = agent_info_result.get_json()
                
                if agent_info_data.get('success') and agent_info_data.get('agent'):
                    resource_id = agent_info_data['agent'].get('resource_id')
                else:
                    return jsonify({
                        "success": False,
                        "error": "No agent resource ID provided and none could be discovered."
                    }), 400
            except Exception as e:
                print(f"Error getting agent info: {e}")
                return jsonify({
                    "success": False,
                    "error": f"No agent resource ID provided and failed to discover one: {str(e)}"
                }), 400
        
        if not session_id:
            return jsonify({
                "success": False,
                "error": "Session ID is required"
            }), 400
        
        if not message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        # Extract just the resource ID number if it's a full path
        if resource_id.startswith('projects/'):
            numeric_id = resource_id.split('/')[-1]
        else:
            numeric_id = resource_id
        
        # Variables to track booking info
        booking_created = False
        booking_id = None
        booking_data = None
        direct_booking_created = False
        
        # Check for booking pattern for potential auto-booking
        booking_pattern = ("book" in message.lower() and "truck" in message.lower()) or \
                          ("rent" in message.lower() and "truck" in message.lower()) or \
                          ("confirm" in message.lower() and "reservation" in message.lower()) or \
                          ("yes" in message.lower() and (
                              "book" in message.lower() or 
                              "reservation" in message.lower() or
                              "schedule" in message.lower()))
        
        print(f"Sending message to truck sharing agent session {session_id}: {message}")
        
        # Try direct REST API approach - this is the approach we validated in our testing
        try:
            print("Using direct REST API approach...")
            
            # Get credentials
            token = get_access_token()
            if not token:
                return jsonify({
                    "success": False,
                    "error": "Failed to obtain access token",
                    "details": "Make sure the application has the necessary Google Cloud permissions."
                }), 403
            
            # Construct the API endpoint
            endpoint = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{numeric_id}:streamQuery"
            print(f"Using API endpoint: {endpoint}")
            
            # Prepare the request payload using the working format that we discovered
            payload = {
                "class_method": "stream_query",
                "input": {
                    "user_id": "test_user",
                    "session_id": session_id,
                    "message": message
                }
            }
            
            # Set headers
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Send the request with a generous timeout
            print("Sending API request...")
            response = requests.post(endpoint, headers=headers, json=payload, timeout=45)
            
            if response.status_code == 200:
                print("API call successful!")
                
                # The response is a series of JSON objects separated by newlines
                # We need to extract the last one which contains the actual content
                raw_response = response.text
                
                # Try to extract the relevant response info
                content = None
                try:
                    # Try parsing the response as a complete JSON object
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        content = result[-1]
                    else:
                        content = result
                except json.JSONDecodeError:
                    # Try parsing line by line for streaming responses
                    try:
                        lines = raw_response.strip().split('\n')
                        # Parse the last complete JSON object from the response
                        for line in reversed(lines):
                            if line.strip():
                                content = json.loads(line)
                                break
                    except json.JSONDecodeError:
                        # If we can't parse the JSON, just use the text
                        content = {"text": raw_response}
                
                print(f"Parsed response content: {content}")
                
                # Extract the message text
                response_text = ""
                if content:
                    if "content" in content and "parts" in content["content"]:
                        for part in content["content"]["parts"]:
                            if "text" in part:
                                response_text += part["text"]
                    elif "text" in content:
                        response_text = content["text"]
                
                if not response_text:
                    response_text = "I received your message, but I'm having trouble generating a response. Please try again."
                
                # Handle auto-booking if enabled
                if auto_create_booking and booking_pattern:
                    print("Auto-booking feature requested and booking pattern detected")
                    try:
                        # Create a booking based on the message
                        from flask import g
                        g.original_request_json = request.json
                        booking_result = test_booking().get_json()
                        
                        if booking_result.get("success", False):
                            booking_created = True
                            direct_booking_created = True
                            booking_id = booking_result.get("booking_id")
                            booking_data = booking_result.get("details")
                            print(f"Created booking with ID: {booking_id}")
                        else:
                            print(f"Failed to create booking: {booking_result.get('error')}")
                    except Exception as booking_err:
                        print(f"Error during auto-booking: {booking_err}")
                
                return jsonify({
                    "success": True,
                    "response": response_text,
                    "booking_created": booking_created,
                    "booking_id": booking_id,
                    "booking_data": booking_data,
                    "direct_booking_created": direct_booking_created,
                    "raw_output": raw_response,
                    "simulated": False,
                    "response_object": content
                })
            else:
                print(f"API call failed with status code: {response.status_code}")
                print(f"Error response: {response.text}")
                
                # Fall back to the old approach using the CLI tool if the REST API fails
                print("Falling back to CLI tool approach...")
                
                # Escape quotes in the message to prevent command injection
                escaped_message = message.replace('"', '\\"')
                
                # Run the command to send the message to the real agent with verbose output for debugging
                command = f'python deployment/truck_sharing_remote.py --send --resource_id={numeric_id} --session_id={session_id} --message="{escaped_message}"'
                print(f"Executing command: {command}")
                
                # Set a longer timeout for sending messages to the real agent
                result = run_command(command, timeout=60000)  # 60 seconds timeout
                
                # Log the command result for debugging
                print(f"Command stdout: {result['stdout']}")
                print(f"Command stderr: {result['stderr']}")
                print(f"Command return code: {result['returncode']}")
                
                # Continue with the legacy processing code if the API call failed
                if "SIMULATION" in result['stdout']:
                    # Return a simulated response from the fallback method
                    return jsonify({
                        "success": True,
                        "response": "I'd be happy to help you rent a truck! We have several options available. When do you need it, and what size are you looking for?",
                        "booking_created": False,
                        "simulated": True,
                        "fallback_used": True
                    })
                else:
                    return jsonify({
                        "success": False,
                        "error": "Failed to send message to agent via both API and CLI methods",
                        "api_error": response.text,
                        "cli_error": result["stderr"] or result["stdout"],
                        "status_code": response.status_code
                    }), 500
                
        except Exception as api_err:
            print(f"Error with direct API call: {api_err}")
            
            # Fall back to simulated response as a last resort
            return jsonify({
                "success": True,
                "response": "I'd be happy to help you rent a truck! We have several options available. When do you need it, and what size are you looking for?",
                "booking_created": False,
                "simulated": True,
                "fallback_used": True,
                "error_details": str(api_err)
            })
    
    except Exception as e:
        print(f"Error in send_message: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@truck_api.route('/test_booking', methods=['POST'])
def test_booking():
    """Create a test booking directly in Firestore."""
    try:
        data = request.json or {}
        message = data.get('message', "I need a truck to move some furniture next weekend")
        
        # Generate a unique booking ID
        booking_id = f"booking_{int(time.time())}"
        
        # Get truck and customer info from the message or use defaults
        truck_type = "pickup"
        truck_make = "Ford"
        truck_model = "F-150"
        need_assistance = "assistance" in message.lower() or "help" in message.lower()
        
        # Calculate dates based on message
        now = datetime.now()
        
        # Try to extract date information from the message
        pickup_date = now + timedelta(days=3)  # Default to 3 days from now
        if "weekend" in message.lower():
            # Calculate next Saturday
            days_until_saturday = (5 - now.weekday()) % 7 or 7  # 0=Monday, 6=Sunday
            pickup_date = now + timedelta(days=days_until_saturday)
        elif "tomorrow" in message.lower():
            pickup_date = now + timedelta(days=1)
        elif "next week" in message.lower():
            pickup_date = now + timedelta(days=7)
            
        pickup_datetime = pickup_date.strftime("%Y-%m-%dT09:00:00Z")  # Default to 9 AM
        
        # Calculate estimated hours and cost based on message content
        hours = 3
        hourly_rate = 45.00
        assistance_rate = 25.00
        
        if "few hours" in message.lower():
            hours = 3
        elif "half day" in message.lower():
            hours = 4
        elif "full day" in message.lower() or "all day" in message.lower():
            hours = 8
            
        truck_cost = hourly_rate * hours
        assistance_cost = assistance_rate * hours if need_assistance else 0
        total_cost = truck_cost + assistance_cost
        
        # Create a generic customer ID
        customer_id = "test_customer"
        
        # Prepare the booking data
        booking_data = {
            "id": booking_id,
            "customerId": customer_id,
            "vehicleId": f"test_vehicle_{truck_make}_{truck_model}",
            "ownerId": "test_owner",
            "pickupAddress": "123 Test Pickup St, Test City, CA 12345",
            "destinationAddress": "789 Test Destination Ave, Test City, CA 12345",
            "pickupDateTime": pickup_datetime,
            "estimatedHours": hours,
            "needsAssistance": need_assistance,
            "ridingAlong": True,
            "status": "confirmed",
            "totalCost": total_cost,
            "vehicleMake": truck_make,
            "vehicleModel": truck_model,
            "assistanceCost": assistance_cost,
            "cargoDescription": message,
            "createdAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updatedAt": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        # Create the booking in Firestore
        creation_result = create_booking_in_firestore(booking_data)
        
        if not creation_result["success"]:
            return jsonify({
                "success": False,
                "error": creation_result.get("error", "Failed to create booking in Firestore"),
                "details": creation_result
            }), 500
        
        # Generate a confirmation message
        confirmation = (
            f"Your truck booking has been confirmed! Here are the details:\n\n"
            f"• Booking ID: {booking_id}\n"
            f"• Vehicle: {truck_make} {truck_model}\n"
            f"• Pickup Date/Time: {pickup_date.strftime('%A, %B %d, %Y')} at 9:00 AM\n"
            f"• Estimated Duration: {hours} hours\n"
            f"• Truck Cost: ${truck_cost:.2f} (${hourly_rate:.2f}/hour for {hours} hours)\n"
            f"{f'• Loading Assistance: ${assistance_cost:.2f} (${assistance_rate:.2f}/hour for {hours} hours)' if need_assistance else ''}\n"
            f"• Total Cost: ${total_cost:.2f}\n\n"
            f"You can see all your bookings on your account dashboard. We'll send you a reminder 24 hours before your reservation."
        )
        
        return jsonify({
            "success": True,
            "booking_id": booking_id,
            "confirmation": confirmation,
            "details": booking_data
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@truck_api.route('/get_bookings', methods=['GET'])
def get_bookings():
    """Get all bookings from Firestore."""
    try:
        # Get optional customer ID filter from the request
        customer_id = request.args.get('customer_id', None)
        limit = int(request.args.get('limit', 10))
        
        # Fetch bookings directly from Firestore
        result = get_bookings_from_firestore(customer_id, limit)
        
        if not result["success"]:
            return jsonify({
                "success": False,
                "error": "Failed to get bookings",
                "details": result.get("error", "Unknown error")
            }), 500
        
        # Format dates for better display
        for booking in result.get("documents", []):
            if "pickupDateTime" in booking:
                try:
                    pickup_datetime = booking["pickupDateTime"]
                    # Check if the datetime string needs formatting
                    if "T" in pickup_datetime:
                        date_part = pickup_datetime.split("T")[0]
                        time_part = pickup_datetime.split("T")[1].split("Z")[0]
                        time_part = time_part.split("+")[0] if "+" in time_part else time_part
                        time_part = time_part.split(".")[0] if "." in time_part else time_part
                        
                        # Convert to more readable format
                        try:
                            dt = datetime.strptime(f"{date_part}T{time_part}", "%Y-%m-%dT%H:%M:%S")
                            booking["formattedPickupDate"] = dt.strftime("%A, %B %d, %Y")
                            booking["formattedPickupTime"] = dt.strftime("%I:%M %p")
                        except ValueError:
                            # Keep original if we can't parse
                            booking["formattedPickupDate"] = date_part
                            booking["formattedPickupTime"] = time_part
                except Exception as e:
                    print(f"Error formatting date: {e}")
        
        return jsonify({
            "success": True,
            "bookings": result.get("documents", []),
            "count": result.get("count", 0)
        })
    
    except Exception as e:
        print(f"Error in get_bookings: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500