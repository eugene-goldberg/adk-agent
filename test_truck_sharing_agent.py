#!/usr/bin/env python3
"""
Minimal test script focused only on the truck-sharing agent.
"""

import os
import sys
import json
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines

# Truck sharing agent resource ID from previous deployment
TRUCK_SHARING_AGENT_ID = "1369314189046185984"

def init_vertexai():
    """Initialize Vertex AI with project settings."""
    load_dotenv()
    
    # Always use the pickuptruckapp project
    project_id = "pickuptruckapp"
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    bucket = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET", "gs://pickuptruckapp-bucket")
    
    print(f"Initializing Vertex AI with:")
    print(f"- Project ID: {project_id}")
    print(f"- Location: {location}")
    print(f"- Bucket: {bucket}")
    print(f"- Vertex AI SDK version: {vertexai.__version__ if hasattr(vertexai, '__version__') else 'unknown'}")
    
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=bucket,
    )
    return project_id, location

def get_agent(agent_id):
    """Get the agent by ID."""
    print(f"Getting agent with ID: {agent_id}")
    try:
        remote_agent = agent_engines.get(agent_id)
        print(f"Successfully got agent: {remote_agent.resource_name}")
        return remote_agent
    except Exception as e:
        print(f"Error getting agent: {e}")
        
        # Try with full resource name
        try:
            project_id, location = init_vertexai()
            full_resource_name = f"projects/{project_id}/locations/{location}/reasoningEngines/{agent_id}"
            print(f"Trying with full resource name: {full_resource_name}")
            remote_agent = agent_engines.get(full_resource_name)
            print(f"Successfully got agent: {remote_agent.resource_name}")
            return remote_agent
        except Exception as e2:
            print(f"Error getting agent with full resource name: {e2}")
            return None

def create_session(agent, user_id="test_user"):
    """Create a session for the agent."""
    print(f"Creating session for user: {user_id}")
    try:
        session = agent.create_session(user_id=user_id)
        print(f"Session created:")
        print(f"- Session ID: {session.get('id') if isinstance(session, dict) else session.id}")
        return session
    except Exception as e:
        print(f"Error creating session: {e}")
        
        # Try alternative approach if the first fails
        try:
            from vertexai.preview.reasoning_engines import Session
            print("Trying alternative session creation approach...")
            session = Session(agent, user_id=user_id)
            print(f"Session created (alternative):")
            print(f"- Session ID: {session.id}")
            return session
        except Exception as e2:
            print(f"Error creating session (alternative): {e2}")
            return None

def test_query(agent, session, message="Hello! I need to rent a truck."):
    """Test sending a query to the agent."""
    print(f"Testing query with message: {message}")
    
    # Try standard query approach
    try:
        print("Attempting query method...")
        user_id = session.get('user_id') if isinstance(session, dict) else session.user_id
        session_id = session.get('id') if isinstance(session, dict) else session.id
        
        response = agent.query(
            user_id=user_id,
            session_id=session_id,
            input=message
        )
        print(f"Query response: {response}")
        return True
    except AttributeError as attr_err:
        print(f"query method not available: {attr_err}")
    except Exception as e:
        print(f"Error with query: {e}")
    
    # Try stream_query approach
    try:
        print("Attempting stream_query method...")
        user_id = session.get('user_id') if isinstance(session, dict) else session.user_id
        session_id = session.get('id') if isinstance(session, dict) else session.id
        
        for event in agent.stream_query(
            user_id=user_id,
            session_id=session_id,
            message=message
        ):
            print(f"Stream event: {event}")
        return True
    except AttributeError as attr_err:
        print(f"stream_query method not available: {attr_err}")
    except Exception as e:
        print(f"Error with stream_query: {e}")
    
    # Try direct API call using the REST API
    try:
        print("Attempting direct REST API call...")
        
        import requests
        import google.auth
        import google.auth.transport.requests
        
        # Get credentials
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        token = credentials.token
        
        project_id, location = init_vertexai()
        
        # Extract session and user IDs
        user_id = session.get('user_id') if isinstance(session, dict) else session.user_id
        session_id = session.get('id') if isinstance(session, dict) else session.id
        
        # Try different endpoints
        endpoints = [
            f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/reasoningEngines/{TRUCK_SHARING_AGENT_ID}:query",
            f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{location}/reasoningEngines/{TRUCK_SHARING_AGENT_ID}:query",
            f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/reasoningEngines/{TRUCK_SHARING_AGENT_ID}:streamQuery",
            f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project_id}/locations/{location}/reasoningEngines/{TRUCK_SHARING_AGENT_ID}:streamQuery",
        ]
        
        for i, endpoint in enumerate(endpoints):
            print(f"Trying endpoint {i+1}/{len(endpoints)}: {endpoint}")
            
            # Try with different payload formats
            payloads = [
                {"class_method": "query", "input": {"user_id": user_id, "session_id": session_id, "message": message}},
                {"class_method": "stream_query", "input": {"user_id": user_id, "session_id": session_id, "message": message}},
                {"input": message, "user_id": user_id, "session_id": session_id},
                {"messages": [{"author": "user", "content": message}], "user_id": user_id, "session_id": session_id},
            ]
            
            for j, payload in enumerate(payloads):
                print(f"  Trying payload {j+1}/{len(payloads)}: {json.dumps(payload)}")
                
                # Set headers
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                # Send the request
                try:
                    response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        print(f"API call successful! Status: {response.status_code}")
                        result = response.json()
                        print(f"API Response: {json.dumps(result, indent=2)}")
                        return True
                    else:
                        print(f"API call failed with status code: {response.status_code}")
                        print(f"Error response: {response.text}")
                except Exception as e:
                    print(f"Error with API request: {e}")
        
        return False
    except Exception as e:
        print(f"Error with direct API call: {e}")
        return False

def main():
    """Main function."""
    print("==== Testing Truck Sharing Agent ====")
    
    # Initialize Vertex AI
    init_vertexai()
    
    # Get the agent
    agent = get_agent(TRUCK_SHARING_AGENT_ID)
    if not agent:
        print("Failed to get agent. Exiting.")
        return
    
    # Create a session
    session = create_session(agent)
    if not session:
        print("Failed to create session. Exiting.")
        return
    
    # Test sending a message
    success = test_query(agent, session)
    
    if success:
        print("\n✅ Successfully communicated with the truck-sharing agent!")
    else:
        print("\n❌ Failed to communicate with the truck-sharing agent.")
        
    print("\nComplete agent and session details for debugging:")
    print("-" * 60)
    print(f"Agent resource name: {agent.resource_name}")
    print(f"Agent details: {dir(agent)}")
    print()
    print(f"Session details: {session}")
    
if __name__ == "__main__":
    main()