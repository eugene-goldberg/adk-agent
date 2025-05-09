"""
Agent Discovery and Testing API

This module provides API endpoints for discovering deployed agents in Vertex AI
and testing their functionality with various capabilities.
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
# No default resource ID - will discover agents dynamically

# Set the proper Python path for imports
# This allows execution of commands that need access to the project modules
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Blueprint for agent discovery and testing
agent_api = Blueprint('agent_api', __name__)

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

@agent_api.route('/discover', methods=['GET'])
def discover_agents():
    """Discover agents deployed in Vertex AI."""
    try:
        # Use the list_deployments function from truck_sharing_remote.py via subprocess
        command = f"python deployment/truck_sharing_remote.py --list"
        
        # Set a timeout to prevent hanging
        try:
            result = run_command(command)
        except Exception as timeout_err:
            print(f"Command timed out or failed: {timeout_err}")
            return jsonify({
                "success": False,
                "error": "The operation timed out. Please try again later.",
                "details": str(timeout_err)
            }), 504  # Gateway Timeout
        
        if not result["success"]:
            print(f"Error listing deployments: {result['stderr']}")
            
            # Check for auth errors
            error_message = result["stderr"]
            if "permission" in error_message.lower() or "credentials" in error_message.lower() or "authentication" in error_message.lower():
                return jsonify({
                    "success": False,
                    "error": "Authentication error. Please check your Google Cloud credentials.",
                    "details": error_message
                }), 401  # Unauthorized
            
            return jsonify({
                "success": False,
                "error": f"Failed to list deployments",
                "details": error_message
            }), 500
            
        # Parse output to extract deployment information
        output = result["stdout"]
        print(f"Deployment listing output: {output}")
        
        # Extract information about deployed agents
        agents = []
        found_in_listing = False
        
        # Extract all resource IDs from the output using regex
        matches = re.findall(r'projects/[^/]+/locations/[^/]+/reasoningEngines/(\d+)', output)
        
        if matches:
            found_in_listing = True
            for agent_id in matches:
                # Check for agent type indicators in the output nearby this ID
                agent_type = "unknown"
                display_name = f"Agent {agent_id}"
                description = "A deployed agent in Vertex AI"
                
                # Look for context around this agent ID to determine its type
                id_idx = output.find(agent_id)
                if id_idx >= 0:
                    context = output[max(0, id_idx-100):min(len(output), id_idx+100)]
                    
                    if "truck" in context.lower() or "truck-sharing" in context.lower():
                        agent_type = "truck-sharing-agent"
                        display_name = "Truck Sharing Agent"
                        description = "A pickup truck sharing assistant that helps customers book trucks, find suitable vehicles for their needs, get weather information for moving dates, and manage their bookings."
                    elif "customer" in context.lower() or "service" in context.lower():
                        agent_type = "customer-service-agent"
                        display_name = "Customer Service Agent"
                        description = "A customer service agent that handles various inquiries and support requests."
                
                # Add the agent to our list
                agent_info = {
                    "id": agent_id,
                    "resource_id": f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{agent_id}",
                    "python_version": "3.12",
                    "display_name": display_name,
                    "description": description,
                    "agent_type": agent_type,
                    "found_in_listing": True
                }
                agents.append(agent_info)
        
        # Check if we need to try another discovery method
        if not found_in_listing:
            print("Warning: No agents found in the initial listing, trying secondary discovery method")
            
            # Try to find agent IDs in the AGENT_INTEGRATION_NOTES.md file as a fallback
            notes_command = f"cd {PROJECT_ROOT} && cat AGENT_INTEGRATION_NOTES.md"
            notes_result = run_command(notes_command)
            
            if notes_result["success"]:
                notes_output = notes_result["stdout"]
                
                # Look for truck-sharing-agent
                truck_match = re.search(r'truck-sharing-agent.*?projects/[^/]+/locations/[^/]+/reasoningEngines/(\d+)', notes_output, re.DOTALL)
                if truck_match:
                    truck_agent_id = truck_match.group(1)
                    agents.append({
                        "id": truck_agent_id,
                        "resource_id": f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{truck_agent_id}",
                        "python_version": "3.12",
                        "display_name": "Truck Sharing Agent",
                        "description": "A pickup truck sharing assistant that helps customers book trucks, find suitable vehicles for their needs, get weather information for moving dates, and manage their bookings.",
                        "agent_type": "truck-sharing-agent",
                        "found_in_listing": False,
                        "discovery_method": "integration_notes"
                    })
                    found_in_listing = True
                
                # Look for customer-service-agent
                customer_match = re.search(r'customer-service-agent.*?projects/[^/]+/locations/[^/]+/reasoningEngines/(\d+)', notes_output, re.DOTALL)
                if customer_match:
                    customer_agent_id = customer_match.group(1)
                    agents.append({
                        "id": customer_agent_id,
                        "resource_id": f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{customer_agent_id}",
                        "python_version": "3.12",
                        "display_name": "Customer Service Agent",
                        "description": "A customer service agent that handles various inquiries and support requests.",
                        "agent_type": "customer-service-agent",
                        "found_in_listing": False,
                        "discovery_method": "integration_notes"
                    })
                    found_in_listing = True
        
        # Return warning if no agents were found at all
        if not found_in_listing:
            print("Warning: No agents found through any discovery method")
        
        return jsonify({
            "success": True,
            "agents": agents,
            "agent_count": len(agents),
            "using_defaults": not found_in_listing
        })
    
    except FileNotFoundError as e:
        print(f"File or command not found: {e}")
        return jsonify({
            "success": False,
            "error": "The required script file was not found",
            "details": str(e)
        }), 500
    except PermissionError as e:
        print(f"Permission error: {e}")
        return jsonify({
            "success": False,
            "error": "Permission denied when attempting to list agents",
            "details": str(e)
        }), 403  # Forbidden
    except Exception as e:
        print(f"Error in discover_agents: {e}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred while discovering agents",
            "details": str(e)
        }), 500

@agent_api.route('/create_session', methods=['POST'])
def create_agent_session():
    """Create a session with a Vertex AI agent."""
    try:
        data = request.json or {}
        resource_id = data.get('resource_id')
        
        # If no resource ID provided, try to discover one
        if not resource_id:
            try:
                # Get a list of available agents
                discover_response = discover_agents()
                discover_data = json.loads(discover_response.get_data(as_text=True))
                
                if discover_data.get('success') and discover_data.get('agents'):
                    # Try to find a truck-sharing-agent first (since this is the most suitable for most endpoints)
                    truck_agent = next((agent for agent in discover_data['agents'] 
                                      if agent.get('agent_type') == 'truck-sharing-agent'), None)
                    
                    if truck_agent:
                        resource_id = truck_agent.get('resource_id')
                    else:
                        # Use the first available agent as a fallback
                        resource_id = discover_data['agents'][0].get('resource_id')
                else:
                    return jsonify({
                        "success": False,
                        "error": "No resource ID provided and no agents discovered"
                    }), 400
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Resource ID is required. Failed to discover agents: {str(e)}"
                }), 400
        
        if not resource_id:
            return jsonify({
                "success": False,
                "error": "Resource ID is required and could not be discovered automatically"
            }), 400
        
        # Use the full resource ID if it starts with 'projects/', otherwise construct it
        if not resource_id.startswith('projects/'):
            resource_id = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{resource_id}"
        
        # Run the command to create a session
        command = f"python deployment/truck_sharing_remote.py --create_session --resource_id={resource_id}"
        result = run_command(command)
        
        if not result["success"]:
            return jsonify({
                "success": False,
                "error": "Failed to create session",
                "details": result["stderr"] or "Unknown error"
            }), 500
        
        # Extract the session ID from the output
        session_id = extract_session_id(result["stdout"])
        
        if not session_id:
            return jsonify({
                "success": False,
                "error": "Failed to extract session ID from output",
                "output": result["stdout"]
            }), 500
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "resource_id": resource_id
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_api.route('/send_message', methods=['POST'])
def send_message():
    """Send a message to a Vertex AI agent session."""
    try:
        # Validate request data
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        resource_id = data.get('resource_id')
        session_id = data.get('session_id')
        message = data.get('message')
        
        # If no resource ID provided, try to discover one
        if not resource_id:
            try:
                # Get a list of available agents
                discover_response = discover_agents()
                discover_data = json.loads(discover_response.get_data(as_text=True))
                
                if discover_data.get('success') and discover_data.get('agents'):
                    # Try to find a truck-sharing-agent first for message endpoints
                    truck_agent = next((agent for agent in discover_data['agents'] 
                                      if agent.get('agent_type') == 'truck-sharing-agent'), None)
                    
                    if truck_agent:
                        resource_id = truck_agent.get('resource_id')
                    else:
                        # Use the first available agent as a fallback
                        resource_id = discover_data['agents'][0].get('resource_id')
                else:
                    return jsonify({
                        "success": False,
                        "error": "No resource ID provided and no agents discovered"
                    }), 400
            except Exception as e:
                print(f"Error auto-discovering agents: {e}")
                # Continue without setting resource_id
        
        # Validate required fields
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
        
        if not message.strip():
            return jsonify({
                "success": False,
                "error": "Message cannot be empty"
            }), 400
        
        # Extract just the resource ID number if it's a full path
        if resource_id.startswith('projects/'):
            numeric_id = resource_id.split('/')[-1]
        else:
            numeric_id = resource_id
            
        # Use the truck_sharing_remote.py script to send the message to the real agent
        print(f"Sending message to session {session_id}: {message}")
        
        # Escape quotes in the message to prevent command injection
        escaped_message = message.replace('"', '\\"')
        
        # Set up the command
        command = f'python deployment/truck_sharing_remote.py --send --resource_id={numeric_id} --session_id={session_id} --message="{escaped_message}"'
        
        # Run the command with timeout handling
        try:
            result = run_command(command)
        except Exception as command_err:
            print(f"Command execution failed: {command_err}")
            return jsonify({
                "success": False,
                "error": "Failed to execute command",
                "details": str(command_err)
            }), 500
        
        # Check for command execution failure
        if not result["success"]:
            print(f"Error sending message to agent: {result['stderr']}")
            error_message = result["stderr"] or "Unknown error"
            
            # Check for specific error types
            if "Session not found" in error_message or "Invalid session" in error_message:
                return jsonify({
                    "success": False,
                    "error": "Invalid or expired session",
                    "details": error_message,
                    "code": "SESSION_EXPIRED"
                }), 404
            elif "Authentication" in error_message or "auth" in error_message.lower() or "credentials" in error_message.lower():
                return jsonify({
                    "success": False,
                    "error": "Authentication error",
                    "details": error_message,
                    "code": "AUTH_ERROR"
                }), 401
            elif "timeout" in error_message.lower() or "timed out" in error_message.lower():
                return jsonify({
                    "success": False,
                    "error": "The request timed out",
                    "details": error_message,
                    "code": "TIMEOUT"
                }), 504
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to send message",
                    "details": error_message,
                    "code": "AGENT_ERROR"
                }), 500
        
        # Extract the response from the output
        output = result["stdout"]
        print(f"Agent response output: {output}")
        
        # Check for empty output
        if not output or not output.strip():
            return jsonify({
                "success": False,
                "error": "Agent returned empty response",
                "code": "EMPTY_RESPONSE"
            }), 500
        
        # Try to extract the response content from the output
        try:
            # First check if there's a "Response:" marker
            if "Response:" in output:
                response_content = output.split("Response:", 1)[1].strip()
            else:
                # Look for response text in JSON format
                text_matches = re.findall(r'"text": "([^"]*)"', output)
                
                if text_matches:
                    # Join all text matches
                    response_content = "\n".join([text.replace('\\n', '\n').replace('\\\"', '"') for text in text_matches])
                elif "Output:" in output:
                    # Try to extract content after "Output:" marker
                    response_content = output.split("Output:", 1)[1].strip()
                else:
                    # If all else fails, just return the raw output
                    response_content = output.strip()
            
            # Final check for empty response after processing
            if not response_content or not response_content.strip():
                return jsonify({
                    "success": False,
                    "error": "Failed to extract meaningful response from agent output",
                    "raw_output": output,
                    "code": "PARSING_ERROR"
                }), 500
            
            # Return successful response
            return jsonify({
                "success": True,
                "response": response_content,
                "raw_output": output,
                "session_id": session_id,
                "resource_id": resource_id
            })
        except Exception as e:
            print(f"Error parsing agent response: {e}")
            # If we can't parse the response, return the raw output
            return jsonify({
                "success": True,
                "response": output.strip(),
                "raw_output": output,
                "parse_error": str(e),
                "note": "Returning raw output due to parsing error"
            })
    
    except Exception as e:
        print(f"Exception in send_message: {e}")
        # Provide more specific error response based on exception type
        if isinstance(e, (ValueError, TypeError)):
            return jsonify({
                "success": False,
                "error": "Invalid request data",
                "details": str(e),
                "code": "INVALID_DATA"
            }), 400
        elif isinstance(e, FileNotFoundError):
            return jsonify({
                "success": False,
                "error": "Required file not found",
                "details": str(e),
                "code": "FILE_NOT_FOUND"
            }), 500
        else:
            return jsonify({
                "success": False,
                "error": "An unexpected error occurred",
                "details": str(e),
                "code": "UNEXPECTED_ERROR"
            }), 500

@agent_api.route('/test_features', methods=['POST'])
def test_features():
    """Test various features of a Vertex AI agent."""
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "Request body is required"
            }), 400
        
        resource_id = data.get('resource_id')
        session_id = data.get('session_id')
        features = data.get('features', [])
        
        # If no resource ID provided, try to discover one
        if not resource_id:
            try:
                # Get a list of available agents
                discover_response = discover_agents()
                discover_data = json.loads(discover_response.get_data(as_text=True))
                
                if discover_data.get('success') and discover_data.get('agents'):
                    # For test_features, prefer truck-sharing-agent as it has more capabilities
                    truck_agent = next((agent for agent in discover_data['agents'] 
                                     if agent.get('agent_type') == 'truck-sharing-agent'), None)
                    
                    if truck_agent:
                        resource_id = truck_agent.get('resource_id')
                    else:
                        # Use the first available agent as a fallback
                        resource_id = discover_data['agents'][0].get('resource_id')
                else:
                    return jsonify({
                        "success": False,
                        "error": "No resource ID provided and no agents discovered"
                    }), 400
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Resource ID is required. Failed to discover agents: {str(e)}"
                }), 400
        
        if not session_id:
            return jsonify({
                "success": False,
                "error": "Session ID is required"
            }), 400
        
        if not features:
            return jsonify({
                "success": False,
                "error": "At least one feature to test is required"
            }), 400
        
        # Extract just the resource ID number if it's a full path
        if resource_id.startswith('projects/'):
            numeric_id = resource_id.split('/')[-1]
        else:
            numeric_id = resource_id
        
        # Map of feature names to test messages
        feature_messages = {
            "basic": "Hello, I need a pickup truck this weekend for moving some furniture. What options do you have?",
            "weather": "I need to move next Saturday. What will the weather be like in Boston, and would you recommend an open-bed truck or one with a covered bed?",
            "cart": "Yes, I'd like the Ford F-150 with the loading assistance option. Also, can you book it for Saturday from 9am to 3pm?",
            "booking": "Yes, Saturday June 1st from 9am to 3pm works for me.",
            "booking_confirm": "Yes, I'll take the 6-hour rental package. That works perfect for me.",
            "firestore_store": "Yes, please send me the confirmation details. Also, could you store my booking in the Firestore database?",
            "firestore_retrieve": "Could you show me all my truck bookings in the Firestore database?",
            "firestore_detail": "Could you tell me more about my most recent truck booking?"
        }
        
        # Results for each feature test
        results = {}
        
        # Test each requested feature with the real agent
        for feature in features:
            if feature not in feature_messages:
                results[feature] = {
                    "success": False,
                    "error": f"Unknown feature: {feature}",
                    "message_sent": "Feature not supported"
                }
                continue
            
            message = feature_messages[feature]
            
            print(f"Testing feature '{feature}' with message: {message}")
            
            # Escape quotes in the message to prevent command injection
            escaped_message = message.replace('"', '\\"')
            
            # Run the command to send the message to the real agent
            command = f'python deployment/truck_sharing_remote.py --send --resource_id={numeric_id} --session_id={session_id} --message="{escaped_message}"'
            result = run_command(command)
            
            if not result["success"]:
                print(f"Error testing feature '{feature}': {result['stderr']}")
                results[feature] = {
                    "success": False,
                    "error": f"Failed to test feature: {result['stderr'] or 'Unknown error'}",
                    "message_sent": message
                }
                continue
            
            # Extract the response from the output
            output = result["stdout"]
            print(f"Feature '{feature}' response output: {output}")
            
            # Try to extract the response content from the output
            try:
                # First check if there's a "Response:" marker
                if "Response:" in output:
                    response_content = output.split("Response:", 1)[1].strip()
                else:
                    # Look for response text in JSON format
                    text_matches = re.findall(r'"text": "([^"]*)"', output)
                    
                    if text_matches:
                        # Join all text matches
                        response_content = "\n".join([text.replace('\\n', '\n').replace('\\\"', '"') for text in text_matches])
                    elif "Output:" in output:
                        # Try to extract content after "Output:" marker
                        response_content = output.split("Output:", 1)[1].strip()
                    else:
                        # If all else fails, just return the raw output
                        response_content = output.strip()
                
                results[feature] = {
                    "success": True,
                    "response": response_content,
                    "message_sent": message,
                    "raw_output": output
                }
            except Exception as e:
                print(f"Error parsing response for feature '{feature}': {e}")
                results[feature] = {
                    "success": True,  # Still return success since we got a response
                    "response": output,  # Use raw output as response
                    "message_sent": message,
                    "raw_output": output,
                    "parse_error": str(e)
                }
            
            # Sleep to avoid rate limiting
            time.sleep(2)
        
        return jsonify({
            "success": True,
            "results": results
        })
    
    except Exception as e:
        print(f"Exception in test_features: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500