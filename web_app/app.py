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

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
RESOURCE_ID = os.getenv("AGENT_RESOURCE_ID", "1818126039411326976")
API_ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"

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
    # For testing without a live agent, you can use this mock function
    if os.getenv("MOCK_AGENT", "false").lower() == "true":
        print("Using mock agent - creating mock session")
        return str(uuid.uuid4())
    
    session_id = str(uuid.uuid4())
    
    url = f"{API_ENDPOINT}/sessions?session_id={session_id}"
    
    token = get_access_token()
    if token is None:
        print("WARNING: No access token available. Using mock session.")
        return session_id
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Creating session with URL: {url}")
        response = requests.post(url, headers=headers)
        
        print(f"Session creation response: {response.status_code}")
        if response.text:
            print(f"Response text: {response.text[:200]}...")
        
        if response.status_code == 200:
            return session_id
        else:
            print(f"Error creating session: {response.status_code}, {response.text}")
            # For testing purposes, return a session ID anyway
            if os.getenv("TESTING", "false").lower() == "true":
                print("TESTING mode: returning mock session ID despite error")
                return session_id
            return None
    except Exception as e:
        print(f"Exception during session creation: {e}")
        # For testing purposes, return a session ID anyway
        if os.getenv("TESTING", "false").lower() == "true":
            print("TESTING mode: returning mock session ID despite error")
            return session_id
        return None

def send_message_to_agent(session_id, message):
    """Send a message to the Vertex AI agent and get a response."""
    # For testing without a live agent, you can use this mock function
    if os.getenv("MOCK_AGENT", "false").lower() == "true":
        print(f"Using mock agent - responding to: {message}")
        if "weather" in message.lower():
            return "It's currently sunny in Las Vegas with a temperature of 85°F. The forecast for the next few days shows continued clear skies with temperatures ranging from 82-90°F."
        elif "plant" in message.lower() or "garden" in message.lower():
            return "For a dry climate like Las Vegas, I recommend drought-resistant plants such as agave, yucca, and various cacti. You might also consider desert marigolds or lantana for adding some color to your garden."
        elif "hello" in message.lower() or "hi" in message.lower():
            return "Hello! I'm the Cymbal Home & Garden Customer Service agent. How can I help you today?"
        else:
            return "Thank you for your message. As a customer service agent for Cymbal Home & Garden, I'm here to help with your gardening and home improvement needs. Is there something specific you'd like assistance with?"
    
    url = f"{API_ENDPOINT}/sessions/{session_id}:reason"
    
    token = get_access_token()
    if token is None:
        print("WARNING: No access token available. Using mock response.")
        return "I'm sorry, I'm having trouble connecting to my knowledge base right now. How else can I help you?"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {"author": "user", "content": message}
        ],
        "enableOrchestration": True
    }
    
    try:
        print(f"Sending message to URL: {url}")
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"Message response: {response.status_code}")
        if response.text:
            print(f"Response text preview: {response.text[:200]}...")
        
        if response.status_code == 200:
            data = response.json()
            # Extract the last response from the agent
            agent_responses = []
            for message in data.get("messages", []):
                if message.get("author") == "customer_service_agent" and "content" in message:
                    content = message.get("content", {}).get("parts", [{}])[0].get("text", "")
                    if content:
                        agent_responses.append(content)
            
            # Return the last non-empty response or a default message
            return agent_responses[-1] if agent_responses else "Sorry, I couldn't process your request."
        else:
            print(f"Error sending message: {response.status_code}, {response.text}")
            # For testing purposes, return a mock response
            if os.getenv("TESTING", "false").lower() == "true":
                print("TESTING mode: returning mock response despite error")
                return f"This is a mock response for testing. You said: {message}"
            return "Sorry, there was an error communicating with the agent."
    except Exception as e:
        print(f"Exception during message sending: {e}")
        # For testing purposes, return a mock response
        if os.getenv("TESTING", "false").lower() == "true":
            print("TESTING mode: returning mock response despite error")
            return f"This is a mock response for testing. You said: {message}"
        return "Sorry, there was an error communicating with the agent."

# API Routes

@app.route('/api/sessions', methods=['POST'])
def api_create_session():
    """API endpoint to create a new session."""
    # For testing, always mock and succeed
    if os.getenv("TESTING", "false").lower() == "true" or os.getenv("MOCK_AGENT", "false").lower() == "true":
        print("TESTING/MOCK mode: Creating mock session")
        mock_session_id = str(uuid.uuid4())
        session['session_id'] = mock_session_id
        session['messages'] = []
        return jsonify({
            'success': True,
            'session_id': mock_session_id
        })
    
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
    
    # For testing, always mock and succeed
    if os.getenv("TESTING", "false").lower() == "true" or os.getenv("MOCK_AGENT", "false").lower() == "true":
        print(f"TESTING/MOCK mode: Processing message: {user_message}")
        
        # Add user message to chat history if using server-side session
        if 'messages' not in session:
            session['messages'] = []
            
        session['messages'].append({
            'author': 'user',
            'content': user_message
        })
        
        # Generate mock response based on message content
        if "weather" in user_message.lower():
            mock_response = "It's currently sunny in Las Vegas with a temperature of 85°F. The forecast for the next few days shows continued clear skies with temperatures ranging from 82-90°F."
        elif "plant" in user_message.lower() or "garden" in user_message.lower():
            mock_response = "For a dry climate like Las Vegas, I recommend drought-resistant plants such as agave, yucca, and various cacti. You might also consider desert marigolds or lantana for adding some color to your garden."
        elif "hello" in user_message.lower() or "hi" in user_message.lower():
            mock_response = "Hello! I'm the Cymbal Home & Garden Customer Service agent. How can I help you today?"
        else:
            mock_response = f"Thank you for your message: '{user_message}'. As a customer service agent for Cymbal Home & Garden, I'm here to help with your gardening and home improvement needs. Is there something specific you'd like assistance with?"
        
        # Add mock response to chat history
        session['messages'].append({
            'author': 'agent',
            'content': mock_response
        })
        session.modified = True
        
        return jsonify({
            'success': True,
            'response': mock_response
        })
    
    # Normal processing for non-testing mode
    # Add user message to chat history if using server-side session
    if session.get('session_id') == session_id and 'messages' in session:
        session['messages'].append({
            'author': 'user',
            'content': user_message
        })
    
    # Get response from agent
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

@app.route('/api/sessions/<session_id>/messages', methods=['GET'])
def api_get_messages(session_id):
    """API endpoint to get all messages for a session."""
    # For testing, always mock and succeed
    if os.getenv("TESTING", "false").lower() == "true" or os.getenv("MOCK_AGENT", "false").lower() == "true":
        print(f"TESTING/MOCK mode: Getting messages for session: {session_id}")
        
        if 'messages' in session:
            messages = session['messages']
        else:
            # Create some sample messages
            messages = [
                {
                    'author': 'agent',
                    'content': 'Welcome to Cymbal Home & Garden! How can I help you today?'
                }
            ]
            session['messages'] = messages
        
        return jsonify({
            'success': True,
            'messages': messages
        })
    
    # Normal processing for non-testing mode
    if session.get('session_id') == session_id and 'messages' in session:
        return jsonify({
            'success': True,
            'messages': session['messages']
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Session not found or no messages'
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

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run the Customer Service Agent web app')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
    args = parser.parse_args()
    
    print(f"Starting server on {args.host}:{args.port}")
    app.run(debug=True, host=args.host, port=args.port, threaded=True)