"""
Test direct interaction with Reasoning Engine API.
"""

import os
from google.api_core.client_options import ClientOptions
from google.cloud.aiplatform_v1 import (
    ReasoningEngineServiceClient,
    ReasoningEngineExecutionServiceClient
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
TRUCK_RESOURCE_ID = os.getenv("TRUCK_AGENT_RESOURCE_ID", "9202903528392097792")
CUSTOMER_RESOURCE_ID = os.getenv("AGENT_RESOURCE_ID", "1818126039411326976")

def list_reasoning_engines():
    """List all reasoning engines."""
    print("\n=== Listing Reasoning Engines ===")
    
    # Create the client
    client_options = ClientOptions(
        api_endpoint=f"{LOCATION}-aiplatform.googleapis.com"
    )
    client = ReasoningEngineServiceClient(client_options=client_options)
    
    # Format the parent resource
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}"
    print(f"Parent resource: {parent}")
    
    # List the reasoning engines
    try:
        response = client.list_reasoning_engines(parent=parent)
        print(f"Found {len(response.reasoning_engines)} reasoning engines:")
        
        for i, engine in enumerate(response.reasoning_engines):
            print(f"\nReasoning Engine #{i+1}:")
            print(f"  Name: {engine.name}")
            print(f"  Display Name: {engine.display_name}")
            print(f"  Create Time: {engine.create_time}")
            print(f"  Update Time: {engine.update_time}")
            # Add more fields as needed
    except Exception as e:
        print(f"Error listing reasoning engines: {e}")

def create_session(resource_id):
    """Create a session with a reasoning engine."""
    print(f"\n=== Creating Session with Resource ID: {resource_id} ===")
    
    # Create the client
    client_options = ClientOptions(
        api_endpoint=f"{LOCATION}-aiplatform.googleapis.com"
    )
    execution_client = ReasoningEngineExecutionServiceClient(client_options=client_options)
    
    # Format the parent resource
    parent = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{resource_id}"
    print(f"Parent resource: {parent}")
    
    # List all methods available on the client
    print("Available methods on execution client:")
    methods = [name for name in dir(execution_client) if not name.startswith('_') and callable(getattr(execution_client, name))]
    for method in sorted(methods):
        print(f"  - {method}")
    
    # Try to create a session using Python subprocess
    import subprocess
    import json
    
    print("\nTrying to create session with subprocess:")
    try:
        # Use the CLI approach since the API client doesn't seem to have the right method
        session_id = "test_session_" + os.urandom(4).hex()
        cmd = f"python deployment/truck_sharing_remote.py --create_session --resource_id={resource_id}"
        
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True,
            capture_output=True, 
            text=True
        )
        
        print(f"Command output: {result.stdout}")
        
        # Try to extract the session ID from the output
        import re
        session_match = re.search(r'Session ID:\s*(\d+)', result.stdout)
        if session_match:
            session_id = session_match.group(1)
            print(f"Extracted session ID from output: {session_id}")
            return session_id
        
        # If that doesn't work, try another pattern
        session_match = re.search(r'"id":\s*"?(\d+)"?', result.stdout)
        if session_match:
            session_id = session_match.group(1)
            print(f"Extracted session ID from JSON: {session_id}")
            return session_id
            
        # If we can't extract a session ID, return a dummy one for testing
        print("Couldn't extract session ID from output, using generated ID")
        return session_id
    except Exception as e:
        print(f"Error creating session with subprocess: {e}")
        
        # Return a made-up session ID for testing
        session_id = "test_session_" + os.urandom(4).hex()
        print(f"Using made-up session ID for testing: {session_id}")
        return session_id

def send_message(resource_id, session_id, message):
    """Send a message to a reasoning engine session."""
    print(f"\n=== Sending Message to Session: {session_id} ===")
    print(f"Message: {message}")
    
    # Create the client
    client_options = ClientOptions(
        api_endpoint=f"{LOCATION}-aiplatform.googleapis.com"
    )
    client = ReasoningEngineExecutionServiceClient(client_options=client_options)
    
    # Format the session resource name
    session_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{resource_id}/sessions/{session_id}"
    print(f"Session resource: {session_name}")
    
    # Send the message - first try
    print("\nAttempt 1: Using QueryReasoningEngineRequest")
    try:
        # See if the query_reasoning_engine method exists
        if hasattr(client, 'query_reasoning_engine'):
            from google.cloud.aiplatform_v1.types import reasoning_engine
            
            request = reasoning_engine.QueryReasoningEngineRequest(
                reasoning_engine_session=session_name,
                query=message,
                max_depth=5,
            )
            
            print("Sending query...")
            response = client.query_reasoning_engine(request=request)
            
            print("Response received:")
            print(response)
            return response
        else:
            print("Method 'query_reasoning_engine' not found on client")
    except Exception as e:
        print(f"Error sending message (attempt 1): {e}")
    
    # Second try - use REST API directly
    print("\nAttempt 2: Using REST API directly")
    try:
        import requests
        import google.auth
        import google.auth.transport.requests
        
        # Get credentials and project ID
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        token = credentials.token
        
        # Construct the API endpoint
        endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/{session_name}:reason"
        print(f"Using API endpoint: {endpoint}")
        
        # Prepare the request payload
        payload = {
            "messages": [
                {"author": "user", "content": message}
            ],
            "enableOrchestration": True
        }
        
        # Set headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Send the request
        print("Sending API request...")
        response = requests.post(endpoint, headers=headers, json=payload)
        
        print(f"Response status code: {response.status_code}")
        if response.status_code == 200:
            print("API call successful!")
            result = response.json()
            print(f"API Response: {result}")
            return result
        else:
            print(f"API call failed: {response.status_code}")
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error sending message (attempt 2): {e}")
    
    # Third try - use subprocess with CLI
    print("\nAttempt 3: Using subprocess CLI approach")
    try:
        import subprocess
        import re
        
        # Escape quotes in the message
        escaped_message = message.replace('"', '\\"')
        
        # Run the command
        cmd = f'python deployment/truck_sharing_remote.py --send --resource_id={resource_id} --session_id={session_id} --message="{escaped_message}"'
        print(f"Executing command: {cmd}")
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        print(f"Command return code: {result.returncode}")
        print(f"Command output: {result.stdout}")
        
        if result.stderr:
            print(f"Command error: {result.stderr}")
        
        # Try to extract the response from the output
        if "Response:" in result.stdout:
            response = result.stdout.split("Response:", 1)[1].strip()
            print(f"Extracted response: {response}")
            return response
        
        return result.stdout
    except Exception as e:
        print(f"Error sending message (attempt 3): {e}")
        return None

def main():
    """Main function."""
    # List all reasoning engines
    list_reasoning_engines()
    
    # Create session with truck-sharing-agent
    session_id = create_session(TRUCK_RESOURCE_ID)
    if session_id:
        # Extract just the session ID from the full name
        session_id = session_id.split("/")[-1]
        print(f"Extracted session ID: {session_id}")
        
        # Send a message
        send_message(TRUCK_RESOURCE_ID, session_id, "Hello, I need to rent a truck for moving")
    
if __name__ == "__main__":
    main()