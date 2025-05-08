#!/usr/bin/env python3
"""
Simple CLI to test interaction with the deployed truck sharing agent.
"""

import sys
import vertexai
from vertexai import agent_engines
import os
from google.cloud import aiplatform

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_test_cli.py \"<message>\"")
        sys.exit(1)
    
    # Agent parameters
    project_id = "pickuptruckapp"
    location = "us-central1"
    resource_id = "9202903528392097792"
    session_id = "3587306768956391424"
    user_id = "test_user"
    message = sys.argv[1]
    
    # Initialize Vertex AI
    print("Initializing Vertex AI...")
    vertexai.init(project=project_id, location=location)
    
    # Get the agent
    print("Getting agent...")
    agent = agent_engines.get(resource_id)
    print(f"Agent: {agent}")
    
    print("\nAttempting to connect to Vertex AI Reasoning Engines...")
    
    # Try to use the agent engine from the console
    try:
        print("\nUsing web console URL approach:")
        console_url = f"https://console.cloud.google.com/vertex-ai/generative/reasoning-engines/details/{resource_id}?project={project_id}"
        print(f"Visit this URL to test the agent in the web console: {console_url}")
        print(f"\nOnce in the console, you can use this session ID: {session_id}")
        
        # Direct link to the agent testing page
        test_url = f"https://console.cloud.google.com/vertex-ai/generative/reasoning-engines/details/{resource_id}/test?project={project_id}"
        print(f"\nOr use this direct link to the testing page: {test_url}")
        
        print("\nYou can also test the truck sharing agent from the Google Cloud Console.")
        print("The agent should be available at:")
        print(f"https://console.cloud.google.com/vertex-ai/generative/reasoning-engines?project={project_id}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()