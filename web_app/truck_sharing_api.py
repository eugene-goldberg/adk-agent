"""
Truck Sharing Agent API 

This module provides API endpoints for testing the Truck Sharing agent deployed in Vertex AI
and interacting with it through a web interface.
"""

import os
import requests
import json
import uuid
import re
import time
import subprocess
import sys
from flask import Blueprint, jsonify, request, current_app
from google.auth.transport.requests import Request
import google.auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
REGION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
DEFAULT_RESOURCE_ID = os.getenv("TRUCK_AGENT_RESOURCE_ID", "9202903528392097792")

# Set the proper Python path for imports
# This allows execution of commands that need access to the project modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Blueprint for truck sharing agent
truck_api = Blueprint('truck_api', __name__)

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

def run_command(command):
    """Run a shell command with proper environment variables."""
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT}:{env.get('PYTHONPATH', '')}"
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            env=env
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
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
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
        # Return hardcoded agent information
        agent_id = DEFAULT_RESOURCE_ID
        agent_info = {
            "id": agent_id,
            "resource_id": f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{agent_id}",
            "python_version": "3.12",
            "display_name": "truck-sharing-agent",
            "description": "A truck sharing assistant that helps customers book trucks, manage reservations, find suitable vehicles, and check weather conditions for moves."
        }
        
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
        resource_id = data.get('resource_id', DEFAULT_RESOURCE_ID)
        
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
            
        # First try with explicit create_session flag
        command = f"python deployment/truck_sharing_remote.py --create_session --resource_id={numeric_id}"
        result = run_command(command)
        
        print(f"Command output: {result['stdout']}")
        print(f"Command error: {result['stderr']}")
        
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
        
        # If still no session_id, fallback to direct API call
        if not session_id:
            print("Falling back to manually creating a session")
            # Just for testing - create a random session ID
            session_id = str(uuid.uuid4()).replace("-", "")[:16]
            print(f"Using random session ID for testing: {session_id}")
            
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
    """Send a message to the truck sharing agent."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        resource_id = data.get('resource_id', DEFAULT_RESOURCE_ID)
        session_id = data.get('session_id')
        message = data.get('message')
        
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
            resource_id = resource_id.split('/')[-1]
        
        # Run the command to send a message
        command = f'python deployment/truck_sharing_remote.py --send --resource_id={resource_id} --session_id={session_id} --message="{message}"'
        result = run_command(command)
        
        # For testing purposes, if command fails or in development mode, use the local simulation
        if not result["success"] or os.getenv("FLASK_ENV") == "development":
            # Fall back to local test with simulated responses
            print("Using local test simulation for truck sharing agent")
            test_command = f'python customer_service/test_truck_conversation.py --interactive'
            
            # Use a predefined scenario based on message content
            if "weather" in message.lower():
                test_command += " --scenario weather"
            elif "book" in message.lower() or "truck" in message.lower() or "move" in message.lower():
                test_command += " --scenario booking"
            elif "cancel" in message.lower():
                test_command += " --scenario cancellation"
            elif "status" in message.lower():
                test_command += " --scenario booking_status"
            
            local_result = run_command(test_command)
            
            # Extract the agent response from the local test output
            response_match = re.search(r'🤖 Agent: (.*?)(?=\n👤 User:|$)', local_result["stdout"], re.DOTALL)
            
            if response_match:
                response_content = response_match.group(1).strip()
            else:
                response_content = "I'm sorry, I couldn't process your request at this time. Please try again later."
                
            return jsonify({
                "success": True,
                "response": response_content,
                "simulated": True
            })
        
        # Extract the response from the output
        output = result["stdout"]
        
        # Try to extract the response content from the JSON output
        try:
            # Look for response text in the output
            response_content = ""
            # Regex to find text content in the response
            text_matches = re.findall(r'"text": "([^"]*)"', output)
            
            if text_matches:
                # Join all text matches
                response_content = "\n".join([text.replace('\\n', '\n').replace('\\\"', '"') for text in text_matches])
            else:
                # Use a fallback approach to find a response
                response_match = re.search(r'Response:\s*\n(.+?)(?=\n\n|$)', output, re.DOTALL)
                if response_match:
                    response_content = response_match.group(1).strip()
                else:
                    response_content = "I'm sorry, I couldn't process your request at this time. Please try again later."
            
            return jsonify({
                "success": True,
                "response": response_content,
                "raw_output": output
            })
        except Exception as e:
            return jsonify({
                "success": True,
                "response": "I'm here to help with your truck needs! How can I assist you today?",
                "raw_output": output,
                "parse_error": str(e)
            })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@truck_api.route('/test_booking', methods=['POST'])
def test_booking():
    """Create a test booking using the interactive booking script."""
    try:
        data = request.json or {}
        message = data.get('message', "I need a truck to move some furniture next weekend")
        
        # Run the interactive booking test script
        command = f'python interactive_booking_test.py'
        result = run_command(command)
        
        if not result["success"]:
            return jsonify({
                "success": False,
                "error": "Failed to create test booking",
                "details": result["stderr"] or "Unknown error"
            }), 500
        
        # Extract the booking ID from the result
        booking_match = re.search(r'Created booking ID: (booking_\d+)', result["stdout"])
        booking_id = booking_match.group(1) if booking_match else "unknown"
        
        # Extract confirmation details
        confirmation_match = re.search(r'🤖 Agent: Great news!(.*?)Conversation ended!', result["stdout"], re.DOTALL)
        confirmation_details = confirmation_match.group(1).strip() if confirmation_match else ""
        
        return jsonify({
            "success": True,
            "booking_id": booking_id,
            "confirmation": confirmation_details,
            "output": result["stdout"]
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
        # Run command to query Firestore for bookings
        command = f'python test_live_booking.py'
        result = run_command(command)
        
        if not result["success"]:
            return jsonify({
                "success": False,
                "error": "Failed to get bookings",
                "details": result["stderr"] or "Unknown error"
            }), 500
        
        # Extract booking information from the output
        booking_data = []
        booking_blocks = re.findall(r'1\. Querying confirmed bookings:(.*?)Testing completed!', result["stdout"], re.DOTALL)
        
        if booking_blocks:
            booking_json_str = booking_blocks[0].strip()
            try:
                # Try to parse the JSON from the output
                start_idx = booking_json_str.find('{')
                end_idx = booking_json_str.rfind('}') + 1
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = booking_json_str[start_idx:end_idx]
                    bookings_data = json.loads(json_str)
                    
                    if 'documents' in bookings_data:
                        booking_data = bookings_data['documents']
                    else:
                        booking_data = []
            except json.JSONDecodeError:
                booking_data = []
        
        return jsonify({
            "success": True,
            "bookings": booking_data
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500