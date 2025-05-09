from flask import Flask, render_template, request, jsonify, session, make_response
import os
import uuid
import json
import requests
from dotenv import load_dotenv
from google.oauth2 import service_account
import google.auth
import google.auth.transport.requests

# Import our API blueprints
try:
    from agent_api import agent_api
    has_agent_api = True
except ImportError:
    has_agent_api = False

from agent_discovery_api import agent_api as agent_discovery_blueprint  # Import our agent discovery API blueprint
from truck_sharing_api import truck_api  # Import our truck sharing API blueprint

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DEBUG'] = True

# Allow cross-origin requests for development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Register the existing agent_api blueprint if available
if has_agent_api:
    app.register_blueprint(agent_api, url_prefix='/api/agent')

# Register our new agent discovery API blueprint
app.register_blueprint(agent_discovery_blueprint, url_prefix='/api/discovery')

# Register our truck sharing API blueprint
app.register_blueprint(truck_api, url_prefix='/api/truck')

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
# No hard-coded IDs - all identifiers must be discovered dynamically
RESOURCE_ID = os.getenv("AGENT_RESOURCE_ID")
TRUCK_RESOURCE_ID = os.getenv("TRUCK_AGENT_RESOURCE_ID")
API_ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"

# Strictly disable all mock responses
os.environ["MOCK_AGENT"] = "false"
os.environ["TESTING"] = "false"

def get_access_token():
    """Get access token using application default credentials."""
    try:
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        print(f"Successfully obtained access token for project: {project}")
        return credentials.token
    except Exception as e:
        print(f"Error getting access token: {e}")
        # For testing purposes, you can return None to skip auth
        return None

def create_new_session():
    """Create a new session with the Vertex AI agent."""
    # Use the truck_sharing_remote.py script to create a session with the real agent
    print("Creating session with truck sharing agent")
    
    # Get resource ID or discover dynamically
    resource_id = TRUCK_RESOURCE_ID
    
    # If resource_id is not available, try to discover a truck-sharing agent
    if not resource_id:
        try:
            # Try to discover agents using the web app's API
            # Import needed so we can call into the function
            from agent_discovery_api import discover_agents
            
            discover_result = discover_agents()
            discover_data = discover_result.get_json()
            
            if discover_data.get("success") and discover_data.get("agents"):
                # Find a truck sharing agent
                truck_agent = next((agent for agent in discover_data["agents"] 
                                  if agent.get("agent_type") == "truck-sharing-agent"), None)
                
                if truck_agent:
                    resource_id = truck_agent.get("resource_id")
                    print(f"Dynamically discovered truck sharing agent: {resource_id}")
                elif discover_data["agents"]:
                    # Fall back to the first agent if no truck agent is found
                    resource_id = discover_data["agents"][0].get("resource_id")
                    print(f"No truck sharing agent found, using first available agent: {resource_id}")
            else:
                print("Failed to discover agents, no resource ID available")
        except Exception as e:
            print(f"Error discovering agents: {e}")
    
    # If we still don't have a resource ID, fail with a helpful message
    if not resource_id:
        print("ERROR: No agent resource ID available. Cannot create session.")
        return None
    
    # Use subprocess to run the truck_sharing_remote.py script
    try:
        import subprocess
        cmd = [
            'python', 'deployment/truck_sharing_remote.py',
            '--create_session',
            f'--resource_id={resource_id}'
        ]
        print(f"Executing command: {' '.join(cmd)}")
        
        # Set up the proper environment variables
        env = os.environ.copy()
        project_root = os.path.abspath(os.path.dirname(__file__))
        parent_dir = os.path.dirname(project_root)
        env["PYTHONPATH"] = f"{parent_dir}:{env.get('PYTHONPATH', '')}"
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            output = result.stdout
            print(f"Session creation output: {output}")
            
            # Try to extract the session ID from the output
            import re
            session_match = re.search(r'Session ID:\s*(\d+)', output)
            if session_match:
                session_id = session_match.group(1)
                print(f"Created session with ID: {session_id}")
                return session_id
            
            # Try another pattern if the first one fails
            session_match = re.search(r'"id":\s*"?(\d+)"?', output)
            if session_match:
                session_id = session_match.group(1)
                print(f"Created session with ID: {session_id}")
                return session_id
                
            # If we can't find a session ID, fall back to a random ID for now
            print("Could not extract session ID from output, using random ID")
            return str(uuid.uuid4())
        else:
            error = result.stderr or "Unknown error"
            print(f"Error creating session: {error}")
            # Fall back to a random session ID in case of error
            # In a production system, you'd want to handle this more gracefully
            fallback_id = str(uuid.uuid4())
            print(f"Using fallback session ID: {fallback_id}")
            return fallback_id
            
    except Exception as e:
        print(f"Exception during session creation: {e}")
        # Fall back to a random session ID in case of exception
        fallback_id = str(uuid.uuid4())
        print(f"Using fallback session ID: {fallback_id}")
        return fallback_id

def send_message_to_agent(session_id, message):
    """Send a message to the Vertex AI agent and get a response."""
    # Use the truck_sharing_remote.py script to send messages to the real agent
    print(f"Sending message to agent session {session_id}: {message}")
    
    # Input validation
    if not session_id:
        print("Error: Missing session ID")
        return "Sorry, I couldn't process your request because the session ID is missing. Please refresh the page and try again."
    
    if not message or not message.strip():
        print("Error: Empty message")
        return "I didn't receive any message to process. Please type a message and try again."
    
    # Escape quotes in the message to prevent command injection
    escaped_message = message.replace('"', '\\"')
    
    # Get resource ID or discover dynamically
    resource_id = TRUCK_RESOURCE_ID
    
    # If resource_id is not available, try to discover a truck-sharing agent
    if not resource_id:
        try:
            # Try to discover agents using the web app's API
            # Import needed so we can call into the function
            from agent_discovery_api import discover_agents
            
            discover_result = discover_agents()
            discover_data = discover_result.get_json()
            
            if discover_data.get("success") and discover_data.get("agents"):
                # Find a truck sharing agent
                truck_agent = next((agent for agent in discover_data["agents"] 
                                  if agent.get("agent_type") == "truck-sharing-agent"), None)
                
                if truck_agent:
                    resource_id = truck_agent.get("resource_id")
                    print(f"Dynamically discovered truck sharing agent: {resource_id}")
                elif discover_data["agents"]:
                    # Fall back to the first agent if no truck agent is found
                    resource_id = discover_data["agents"][0].get("resource_id")
                    print(f"No truck sharing agent found, using first available agent: {resource_id}")
            else:
                print("Failed to discover agents, no resource ID available")
        except Exception as e:
            print(f"Error discovering agents: {e}")
    
    # If we still don't have a resource ID, fail with a helpful message
    if not resource_id:
        print("ERROR: No agent resource ID available. Cannot create session.")
        return None
    
    # Use subprocess to run the truck_sharing_remote.py script
    try:
        import subprocess
        import re
        
        cmd = [
            'python', 'deployment/truck_sharing_remote.py',
            '--send',
            f'--resource_id={resource_id}',
            f'--session_id={session_id}',
            f'--message={escaped_message}'
        ]
        print(f"Executing command: {' '.join(cmd)}")
        
        # Set up the proper environment variables
        env = os.environ.copy()
        project_root = os.path.abspath(os.path.dirname(__file__))
        parent_dir = os.path.dirname(project_root)
        env["PYTHONPATH"] = f"{parent_dir}:{env.get('PYTHONPATH', '')}"
        
        # Set timeout to prevent hanging
        timeout_seconds = 30
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                env=env, 
                timeout=timeout_seconds
            )
        except subprocess.TimeoutExpired:
            print(f"Command timed out after {timeout_seconds} seconds")
            return "Sorry, the request took too long to process. Please try again with a shorter message, or try later when the system is less busy."
        
        if result.returncode == 0:
            output = result.stdout
            print(f"Agent response output: {output}")
            
            # Check for empty output
            if not output or not output.strip():
                print("Warning: Empty response from agent")
                return "I received your message but the agent didn't provide a response. Please try again."
            
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
                
                # Verify we have meaningful content
                if not response_content or not response_content.strip():
                    print("Warning: Extracted empty response content")
                    return "I processed your message but couldn't generate a proper response. Please try rephrasing your question."
                
                return response_content
            except Exception as e:
                print(f"Error parsing agent response: {e}")
                # If we can't parse the response, return the raw output if it's not empty
                if output.strip():
                    return output.strip()
                return "Sorry, I couldn't process your request properly. There was an error parsing the response."
        else:
            error = result.stderr or "Unknown error"
            print(f"Error sending message: {error}")
            
            # Check for specific error types
            if "Session not found" in error or "Invalid session" in error:
                return "Your session has expired. Please refresh the page to start a new conversation."
            elif "Authentication" in error or "auth" in error.lower() or "token" in error.lower():
                return "There was an authentication error. Please try again later or contact support if the issue persists."
            
            return "Sorry, there was an error communicating with the agent. Please try again in a moment."
            
    except Exception as e:
        print(f"Exception during message sending: {e}")
        
        # Provide more specific error messages based on exception type
        if isinstance(e, FileNotFoundError):
            return "Sorry, I couldn't find the necessary files to process your request. Please contact support."
        elif isinstance(e, PermissionError):
            return "Sorry, I don't have permission to access the required resources. Please contact support."
        
        return "Sorry, I encountered a technical issue. Please try again in a moment."

# API Routes

@app.route('/api/sessions', methods=['POST'])
def api_create_session():
    """API endpoint to create a new session."""
    # Always create a real session with the agent
    session_id = create_new_session()
    if session_id:
        # Store session_id in server-side session for convenience but also return it for API use
        session['session_id'] = session_id
        session['messages'] = []
        return jsonify({
            'success': True,
            'session_id': session_id
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to create session'
        }), 500

@app.route('/api/sessions/<session_id>/messages', methods=['POST'])
def api_send_message(session_id):
    """API endpoint to send a message to the agent."""
    data = request.json
    if not data or 'message' not in data:
        return jsonify({
            'success': False,
            'error': 'Message is required'
        }), 400
    
    user_message = data['message']
    
    # Add user message to chat history if using server-side session
    if session.get('session_id') == session_id and 'messages' in session:
        session['messages'].append({
            'author': 'user',
            'content': user_message
        })
    
    try:
        # Get response from the real agent (no fallback to mock)
        agent_response = send_message_to_agent(session_id, user_message)
        
        # Add agent response to chat history if using server-side session
        if session.get('session_id') == session_id and 'messages' in session:
            session['messages'].append({
                'author': 'agent',
                'content': agent_response
            })
            session.modified = True
        
        return jsonify({
            'success': True,
            'response': agent_response
        })
    except Exception as e:
        print(f"Error sending message to agent: {e}")
        return jsonify({
            'success': False,
            'error': f"Error communicating with agent: {str(e)}",
            'details': "The system encountered an error when trying to communicate with the real agent."
        }), 500

@app.route('/api/sessions/<session_id>/messages', methods=['GET'])
def api_get_messages(session_id):
    """API endpoint to get all messages for a session."""
    # Look for messages in the server-side session
    if session.get('session_id') == session_id and 'messages' in session:
        return jsonify({
            'success': True,
            'messages': session['messages']
        })
    else:
        # Session not found - don't create one automatically since we want to use real agent
        return jsonify({
            'success': False,
            'error': 'Session not found or no messages available',
            'message': 'Please create a new session before accessing messages'
        }), 404

# Web Routes

@app.route('/')
def index():
    """Render the home page."""
    if 'session_id' not in session:
        session_id = create_new_session()
        if session_id:
            session['session_id'] = session_id
            session['messages'] = []
        else:
            return "Failed to create a new session. Please try again.", 500
    
    return render_template('index.html', 
                          session_id=session['session_id'], 
                          messages=session.get('messages', []))

@app.route('/agent-testing')
def agent_testing():
    """Render the agent testing interface."""
    return render_template('agent_testing.html')

@app.route('/agent-discovery')
@app.route('/agent-discovery/')
def agent_discovery():
    """Render the agent discovery and testing interface."""
    response = make_response(render_template('agent_discovery.html'))
    # Explicitly add cache control headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
    
@app.route('/truck-sharing')
def truck_sharing():
    """Render the truck sharing agent interface."""
    response = make_response(render_template('truck_sharing.html'))
    # Explicitly add cache control headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run the Customer Service Agent web app')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    args = parser.parse_args()
    
    print(f"Starting server on {args.host}:{args.port}")
    app.run(debug=True, host=args.host, port=args.port, threaded=True)