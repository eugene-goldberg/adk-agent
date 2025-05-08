#!/usr/bin/env python3
"""
Simplified test for Vertex AI Agent using the REST API directly.

This script tests sending a message to the deployed agent without requiring
the full customer_service module.
"""

import os
import argparse
import uuid
import json
from dotenv import load_dotenv
import requests
import google.auth
import google.auth.transport.requests

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
        return None

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Test interaction with Vertex AI agent")
    parser.add_argument("--message", default="Hello, I'm looking for gardening advice for a desert climate.", help="Message to send to the agent")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Configuration
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    resource_id = os.getenv("AGENT_RESOURCE_ID", "1818126039411326976")
    
    # Full resource path in the format used by the LIST command
    full_resource_path = f"projects/{project_id}/locations/{location}/reasoningEngines/{resource_id}"
    
    # Base URL for API calls
    base_url = f"https://{location}-aiplatform.googleapis.com/v1/{full_resource_path}"
    
    # Get access token
    token = get_access_token()
    if not token:
        print("Failed to get access token. Make sure you're authenticated with gcloud.")
        return
    
    # Set up common headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. First test getting the resource info
    print(f"\n1. Checking resource info for {full_resource_path}...")
    try:
        response = requests.get(base_url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Resource name: {data.get('name')}")
            print(f"Display name: {data.get('displayName')}")
            
            # List available methods
            print("\nAvailable methods:")
            for method in data.get('spec', {}).get('classMethods', []):
                print(f"- {method.get('name')}: {method.get('api_mode', 'standard')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"Exception during resource check: {e}")
        return
    
    # 2. Create a session
    print("\n2. Creating a session...")
    
    # Generate a user ID and session ID
    user_id = f"user_{str(uuid.uuid4())[:8]}"
    session_id = str(uuid.uuid4())
    
    print(f"User ID: {user_id}")
    print(f"Session ID: {session_id}")
    
    create_session_url = f"{base_url}:create_session"
    create_session_payload = {
        "user_id": user_id,
        "session_id": session_id
    }
    
    try:
        response = requests.post(create_session_url, headers=headers, json=create_session_payload)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Session created successfully!")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except ValueError:
                print(f"Response: {response.text}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return
    except Exception as e:
        print(f"Exception during session creation: {e}")
        return
    
    # 3. Send a message
    print(f"\n3. Sending message: {args.message}")
    
    query_url = f"{base_url}:stream_query"
    query_payload = {
        "user_id": user_id,
        "session_id": session_id,
        "message": args.message
    }
    
    try:
        response = requests.post(query_url, headers=headers, json=query_payload)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response from agent:")
            try:
                data = response.json()
                print(f"{json.dumps(data, indent=2)}")
            except ValueError:
                print(f"{response.text}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Exception during message sending: {e}")
        
    print("\nTest completed.")

if __name__ == "__main__":
    main()