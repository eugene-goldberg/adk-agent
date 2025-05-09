#!/usr/bin/env python3
"""
Script to test communication with the deployed agents.
"""

import os
import sys
import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines

def list_deployments():
    """List all deployments."""
    deployments = agent_engines.list()
    if not deployments:
        print("No deployments found.")
        return []
    
    print("Deployments:")
    deployment_list = []
    for deployment in deployments:
        print(f"- {deployment.display_name}: {deployment.resource_name}")
        deployment_list.append({
            "display_name": deployment.display_name,
            "resource_name": deployment.resource_name
        })
    
    return deployment_list

def create_session(resource_id, user_id="test_user"):
    """Create a session for the specified agent."""
    print(f"Creating session for agent {resource_id} with user ID {user_id}...")
    remote_app = agent_engines.get(resource_id)
    remote_session = remote_app.create_session(user_id=user_id)
    
    print("Session created:")
    print(f"  Session ID: {remote_session['id']}")
    print(f"  User ID: {remote_session['user_id']}")
    print(f"  App name: {remote_session['app_name']}")
    
    return remote_session['id']

def test_message(resource_id, user_id, session_id, message):
    """Test sending a message to the agent."""
    print(f"\nSending message to {resource_id}, session {session_id}:")
    print(f"Message: {message}")
    print("Response:")
    
    try:
        # Get the remote app
        remote_app = agent_engines.get(resource_id)
        
        # Try to use stream_query method
        print("Using stream_query method...")
        full_response = ""
        for event in remote_app.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message,
        ):
            print(event)
            if hasattr(event, 'text'):
                full_response += event.text
        
        return True
    
    except Exception as e:
        print(f"Error communicating with agent: {e}")
        
        # Try the REST API approach
        print("Falling back to REST API approach...")
        import requests
        import json
        import google.auth
        import google.auth.transport.requests
        
        # Get credentials
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        token = credentials.token
        
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
        
        # Construct the API endpoint using the correct format for Vertex AI Agent Engine
        endpoint = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/reasoningEngines/{resource_id.split('/')[-1]}:streamQuery"
        print(f"Using API endpoint: {endpoint}")
        
        # Prepare the request payload using the correct format
        payload = {
            "class_method": "stream_query",
            "input": {
                "user_id": user_id,
                "session_id": session_id,
                "message": message
            }
        }
        
        # Set headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Send the request
        response = requests.post(endpoint, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("REST API call successful!")
            result = response.json()
            print(f"API Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"REST API call failed with status code: {response.status_code}")
            print(f"Error response: {response.text}")
            return False

def main():
    """Main function."""
    load_dotenv()

    print("Initializing Vertex AI...")
    # Always use the pickuptruckapp project for Firestore integration
    project_id = "pickuptruckapp"
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET", "gs://pickuptruckapp-bucket")
    
    print(f"Using project ID: {project_id}")
    print(f"Using location: {location}")

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=bucket,
    )

    # List all deployments
    print("\nListing all deployments:")
    deployments = list_deployments()
    
    if not deployments:
        print("No deployments found. Exiting.")
        return
    
    # Test each deployment
    for deployment in deployments:
        display_name = deployment["display_name"]
        resource_id = deployment["resource_name"]
        
        print(f"\n==== Testing {display_name} ====")
        
        # Create a session
        user_id = "test_user"
        session_id = create_session(resource_id, user_id)
        
        # Test with a simple message
        test_message_text = "Hello! How can you help me today?"
        success = test_message(resource_id, user_id, session_id, test_message_text)
        
        if success:
            print(f"\n✅ Successfully communicated with {display_name}")
        else:
            print(f"\n❌ Failed to communicate with {display_name}")

if __name__ == "__main__":
    main()