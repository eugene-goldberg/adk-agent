#!/usr/bin/env python3
"""
Helper script to test Vertex AI Agent Engine API and get documentation.
"""

import vertexai
from vertexai import agent_engines

def main():
    project_id = "pickuptruckapp"
    location = "us-central1"
    resource_id = "9202903528392097792"
    session_id = "3587306768956391424"
    user_id = "test_user"
    message = "I need a pickup truck to move some furniture from downtown to my new apartment this Saturday."
    
    # Initialize Vertex AI
    print("Initializing Vertex AI...")
    vertexai.init(
        project=project_id,
        location=location,
    )
    
    # Get the agent
    print("Getting agent...")
    agent = agent_engines.get(resource_id)
    print(f"Agent: {agent}")
    
    # Print available methods
    print("\nAvailable methods for agent:")
    for method_name in dir(agent):
        if not method_name.startswith('_'):
            try:
                # Get the attribute safely
                attr = object.__getattribute__(agent, method_name)
                
                # Check if it's a method (callable)
                if callable(attr):
                    try:
                        doc = attr.__doc__
                        if doc:
                            doc = doc.split('\n')[0]  # Just the first line
                        print(f"- {method_name}(): {doc}")
                    except:
                        print(f"- {method_name}()")
                else:
                    # It's a property or attribute
                    print(f"- {method_name} (property)")
            except Exception as e:
                print(f"- {method_name} (error: {e})")
    
    # Check the streaming_agent_run_with_events method
    print("\nInspecting streaming_agent_run_with_events method:")
    try:
        import inspect
        sare_method = agent.streaming_agent_run_with_events
        sig = inspect.signature(sare_method)
        print(f"- Signature: {sig}")
        doc = inspect.getdoc(sare_method)
        print(f"- Documentation: {doc}")
    except Exception as e:
        print(f"Error inspecting method: {e}")
    
    # Try to call the API
    print("\nAttempting to call API with user ID and session ID...")
    try:
        # Try to create a session if it doesn't exist
        try:
            print("Creating/getting session...")
            session = agent.get_session(user_id=user_id, session_id=session_id)
            print(f"Session: {session}")
        except Exception as e:
            print(f"Error with session: {e}")
            try:
                print("Creating new session...")
                session = agent.create_session(user_id=user_id)
                session_id = session['id']
                print(f"Created session: {session_id}")
            except Exception as e:
                print(f"Error creating session: {e}")
        
        # Try different approaches to call the API
        print("\nTrying different API call approaches...")
        
        try:
            print("Approach 1: Using streaming_agent_run_with_events with no args...")
            response = agent.streaming_agent_run_with_events()
            for event in response:
                print(f"Event: {event}")
        except Exception as e:
            print(f"Error with approach 1: {e}")
        
        try:
            print("\nApproach 2: Using streaming_agent_run_with_events with session ID only...")
            response = agent.streaming_agent_run_with_events(session_id)
            for event in response:
                print(f"Event: {event}")
        except Exception as e:
            print(f"Error with approach 2: {e}")
            
        try:
            print("\nApproach 3: Using request_json parameter...")
            # Based on the error message, it seems we need to use request_json
            request_json = {
                "session_id": session_id,
                "message": message,
            }
            response = agent.streaming_agent_run_with_events(request_json)
            for event in response:
                print(f"Event: {event}")
        except Exception as e:
            print(f"Error with approach 3: {e}")
            
        try:
            print("\nApproach 4: Using different request_json format...")
            # Try a different format
            request_json = {
                "session": {
                    "id": session_id,
                    "user_id": user_id
                },
                "input": {
                    "text": message
                }
            }
            response = agent.streaming_agent_run_with_events(request_json)
            for event in response:
                print(f"Event: {event}")
        except Exception as e:
            print(f"Error with approach 4: {e}")
        
    except Exception as e:
        print(f"Error calling API: {e}")

if __name__ == "__main__":
    main()