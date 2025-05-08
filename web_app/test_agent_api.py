#!/usr/bin/env python3
"""
Test script for Agent API endpoints.

This script tests the agent discovery, session creation, and feature testing
endpoints of the web application.
"""

import requests
import json
import time
import argparse
import sys
import os

# Default values
DEFAULT_HOST = "http://localhost:5000"
MAX_RETRIES = 3
RETRY_DELAY = 2

def print_heading(heading):
    """Print a formatted heading."""
    print("\n" + "=" * 50)
    print(heading)
    print("=" * 50 + "\n")

def test_discovery_api(host=DEFAULT_HOST, verbose=False):
    """Test the agent discovery API endpoint."""
    print_heading("Testing Agent Discovery API")
    
    endpoint = f"{host}/api/agent/discover"
    
    try:
        print(f"Sending request to: {endpoint}")
        response = requests.get(endpoint)
        
        if verbose:
            print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "agents" in data:
                print(f"Success! Found {len(data['agents'])} agents.")
                
                if verbose:
                    for i, agent in enumerate(data["agents"], 1):
                        print(f"\nAgent {i}:")
                        print(f"  ID: {agent.get('id')}")
                        print(f"  Name: {agent.get('display_name')}")
                        print(f"  Description: {agent.get('description')}")
                
                # Return the first agent's resource ID for further testing
                if data["agents"]:
                    return data["agents"][0]["resource_id"]
            else:
                print("API request succeeded but returned unexpected data.")
                print(json.dumps(data, indent=2))
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
    
    except requests.RequestException as e:
        print(f"Request error: {e}")
    
    return None

def test_session_creation_api(host=DEFAULT_HOST, resource_id=None, verbose=False):
    """Test the session creation API endpoint."""
    print_heading("Testing Session Creation API")
    
    if not resource_id:
        print("Error: No resource ID provided for session creation.")
        return None
    
    endpoint = f"{host}/api/agent/create_session"
    payload = {"resource_id": resource_id}
    
    try:
        print(f"Sending request to: {endpoint}")
        print(f"Resource ID: {resource_id}")
        
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if verbose:
            print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("session_id"):
                print(f"Success! Created session with ID: {data['session_id']}")
                return data["session_id"]
            else:
                print("API request succeeded but returned unexpected data.")
                print(json.dumps(data, indent=2))
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
    
    except requests.RequestException as e:
        print(f"Request error: {e}")
    
    return None

def test_feature_testing_api(host=DEFAULT_HOST, resource_id=None, session_id=None, verbose=False):
    """Test the feature testing API endpoint."""
    print_heading("Testing Features API")
    
    if not resource_id or not session_id:
        print("Error: Resource ID and session ID are required for feature testing.")
        return False
    
    endpoint = f"{host}/api/agent/test_features"
    payload = {
        "resource_id": resource_id,
        "session_id": session_id,
        "features": ["basic", "weather"]  # Testing just a couple of features for speed
    }
    
    try:
        print(f"Sending request to: {endpoint}")
        print(f"Testing features: {', '.join(payload['features'])}")
        
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if verbose:
            print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("results"):
                print("Feature test results:")
                
                for feature, result in data["results"].items():
                    status = "✓ Success" if result.get("success") else "✗ Failed"
                    print(f"  {feature}: {status}")
                    
                    if verbose:
                        if "response" in result:
                            print(f"    Response snippet: {result['response'][:100]}...")
                        if "error" in result:
                            print(f"    Error: {result['error']}")
                
                return True
            else:
                print("API request succeeded but returned unexpected data.")
                print(json.dumps(data, indent=2))
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
    
    except requests.RequestException as e:
        print(f"Request error: {e}")
    
    return False

def test_send_message_api(host=DEFAULT_HOST, resource_id=None, session_id=None, verbose=False):
    """Test the send message API endpoint."""
    print_heading("Testing Send Message API")
    
    if not resource_id or not session_id:
        print("Error: Resource ID and session ID are required for sending messages.")
        return False
    
    endpoint = f"{host}/api/agent/send_message"
    payload = {
        "resource_id": resource_id,
        "session_id": session_id,
        "message": "Hello, I'm looking for recommendations for plants that would do well in a desert climate."
    }
    
    try:
        print(f"Sending request to: {endpoint}")
        print(f"Message: {payload['message']}")
        
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if verbose:
            print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("response"):
                print("Message sent successfully!")
                print(f"Response snippet: {data['response'][:100]}...")
                return True
            else:
                print("API request succeeded but returned unexpected data.")
                print(json.dumps(data, indent=2))
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
    
    except requests.RequestException as e:
        print(f"Request error: {e}")
    
    return False

def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Test the Agent API endpoints")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host URL (default: {DEFAULT_HOST})")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--resource-id", help="Specific resource ID to test with")
    parser.add_argument("--session-id", help="Specific session ID to test with")
    
    args = parser.parse_args()
    
    success = True
    resource_id = args.resource_id
    session_id = args.session_id
    
    # Only run discovery if resource ID isn't provided
    if not resource_id:
        print("No resource ID provided. Running agent discovery...")
        resource_id = test_discovery_api(args.host, args.verbose)
        if not resource_id:
            print("Failed to discover any agents. Cannot continue with testing.")
            return 1
    
    # Only create a session if session ID isn't provided
    if not session_id:
        print("No session ID provided. Creating a new session...")
        session_id = test_session_creation_api(args.host, resource_id, args.verbose)
        if not session_id:
            print("Failed to create a session. Cannot continue with testing.")
            return 1
    
    # Test sending a message
    if not test_send_message_api(args.host, resource_id, session_id, args.verbose):
        print("Send message test failed.")
        success = False
    
    # Test feature testing
    if not test_feature_testing_api(args.host, resource_id, session_id, args.verbose):
        print("Feature testing test failed.")
        success = False
    
    print_heading("Test Summary")
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed.")
    
    print(f"Resource ID: {resource_id}")
    print(f"Session ID: {session_id}")
    
    # Print command for manual testing
    print("\nTo test the agent manually, you can use:")
    print(f"curl -X POST {args.host}/api/agent/send_message \\")
    print('  -H "Content-Type: application/json" \\')
    print(f'  -d \'{{"resource_id": "{resource_id}", "session_id": "{session_id}", "message": "Your message here"}}\'')
    
    # Print URL for web testing
    print(f"\nOr visit {args.host}/agent-testing in your browser to use the web interface.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())