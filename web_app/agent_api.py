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
DEFAULT_RESOURCE_ID = os.getenv("AGENT_RESOURCE_ID", "1818126039411326976")

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

@agent_api.route('/discover', methods=['GET'])
def discover_agents():
    """Discover agents deployed in Vertex AI."""
    try:
        # For debugging - let's directly return the hardcoded agent information we already know
        agent_id = "1818126039411326976"
        agent_info = {
            "id": agent_id,
            "resource_id": f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{agent_id}",
            "created": "2025-05-08T14:22:10.990577Z",
            "updated": "2025-05-08T14:24:36.339561Z",
            "python_version": "3.12",
            "display_name": "customer-service-agent",
            "description": "A customer service agent for Cymbal Home & Garden with Firestore and Weather integrations that helps customers with product recommendations, bookings, and gardening advice."
        }
        
        return jsonify({
            "success": True,
            "agents": [agent_info]
        })
    
    except Exception as e:
        print(f"Error in discover_agents: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@agent_api.route('/create_session', methods=['POST'])
def create_agent_session():
    """Create a session with a Vertex AI agent."""
    try:
        data = request.json or {}
        resource_id = data.get('resource_id', DEFAULT_RESOURCE_ID)
        
        if not resource_id:
            return jsonify({
                "success": False,
                "error": "Resource ID is required"
            }), 400
        
        # Use the full resource ID if it starts with 'projects/', otherwise construct it
        if not resource_id.startswith('projects/'):
            resource_id = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{resource_id}"
        
        # Run the command to create a session
        command = f"python deployment/customer_service_remote.py --create_session --resource_id={resource_id}"
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
        
        # Use the full resource ID if it starts with 'projects/', otherwise construct it
        if not resource_id.startswith('projects/'):
            resource_id = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{resource_id}"
        
        # Run the command to send a message
        command = f'python deployment/customer_service_remote.py --send --resource_id={resource_id} --session_id={session_id} --message="{message}"'
        result = run_command(command)
        
        if not result["success"]:
            return jsonify({
                "success": False,
                "error": "Failed to send message",
                "details": result["stderr"] or "Unknown error"
            }), 500
        
        # Extract the response from the output
        # This is more complex and depends on the format of the output
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
                response_content = "No response text found in the output"
            
            return jsonify({
                "success": True,
                "response": response_content,
                "raw_output": output
            })
        except Exception as e:
            return jsonify({
                "success": True,
                "response": "Could not parse response content",
                "raw_output": output,
                "parse_error": str(e)
            })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
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
        
        resource_id = data.get('resource_id', DEFAULT_RESOURCE_ID)
        session_id = data.get('session_id')
        features = data.get('features', [])
        
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
        
        # Use the full resource ID if it starts with 'projects/', otherwise construct it
        if not resource_id.startswith('projects/'):
            resource_id = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{resource_id}"
        
        # Map of feature names to test messages
        feature_messages = {
            "basic": "Hello, I'm looking for recommendations for plants that would do well in a desert climate.",
            "weather": "I'm interested in both flowers and cacti. What's the weather going to be like in Las Vegas this week, and which plants would be suitable based on the forecast?",
            "cart": "Yes, please replace the standard potting soil with cactus mix and add the bloom-boosting fertilizer. Also, can you create a booking for a planting consultation next Friday at 2pm?",
            "booking": "Yes, Friday May 17th at 2pm works for me.",
            "booking_confirm": "Yes, the afternoon slot from 1-4 PM works perfect for me.",
            "firestore_store": "Yes, please send me the care instructions. Also, could you store my appointment in the Firestore database?",
            "firestore_retrieve": "Could you show me all my bookings in the Firestore database?",
            "firestore_detail": "Could you tell me more about my most recent booking?"
        }
        
        # Results for each feature test
        results = {}
        
        # Test each requested feature
        for feature in features:
            if feature not in feature_messages:
                results[feature] = {
                    "success": False,
                    "error": f"Unknown feature: {feature}"
                }
                continue
            
            message = feature_messages[feature]
            command = f'python deployment/customer_service_remote.py --send --resource_id={resource_id} --session_id={session_id} --message="{message}"'
            result = run_command(command)
            
            if not result["success"]:
                results[feature] = {
                    "success": False,
                    "error": "Command execution failed",
                    "details": result["stderr"] or "Unknown error"
                }
                continue
            
            # Try to extract the response content
            try:
                # Look for text content in the output
                text_matches = re.findall(r'"text": "([^"]*)"', result["stdout"])
                
                if text_matches:
                    # Join all text matches
                    response_content = "\n".join([text.replace('\\n', '\n').replace('\\\"', '"') for text in text_matches])
                else:
                    response_content = "No response text found in the output"
                
                results[feature] = {
                    "success": True,
                    "response": response_content,
                    "message_sent": message
                }
            except Exception as e:
                results[feature] = {
                    "success": False,
                    "error": f"Failed to parse response: {str(e)}",
                    "raw_output": result["stdout"]
                }
            
            # Sleep to avoid rate limiting
            time.sleep(2)
        
        return jsonify({
            "success": True,
            "results": results
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500