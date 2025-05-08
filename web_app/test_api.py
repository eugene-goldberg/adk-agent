#!/usr/bin/env python3
"""
API Testing Script for Customer Service Agent Web App

This script tests the API endpoints of the web application to ensure
they correctly interact with the Vertex AI agent.
"""

import requests
import json
import time
import argparse
import os
import sys
from dotenv import load_dotenv

# Setting environment variables for testing
os.environ["TESTING"] = "true"
os.environ["MOCK_AGENT"] = "true"

# Load environment variables
load_dotenv()

# Default values
DEFAULT_HOST = "http://localhost:5000"
MAX_RETRIES = 3
RETRY_DELAY = 2


def test_api_endpoints(host=DEFAULT_HOST, verbose=False):
    """Test all API endpoints and return results"""
    
    results = {
        "success": True,
        "tests": []
    }
    
    # Test 1: Create a new session
    print("🧪 Testing session creation...")
    session_result = test_create_session(host, verbose)
    results["tests"].append(session_result)
    
    if not session_result["passed"]:
        results["success"] = False
        print("❌ Session creation failed. Skipping remaining tests.")
        return results
    
    session_id = session_result["data"]["session_id"]
    
    # Test 2: Send a message to the agent
    print(f"🧪 Testing message sending with session {session_id[:8]}...")
    message_result = test_send_message(host, session_id, verbose)
    results["tests"].append(message_result)
    
    if not message_result["passed"]:
        results["success"] = False
    
    # Test 3: Get messages for the session
    print(f"🧪 Testing message retrieval with session {session_id[:8]}...")
    messages_result = test_get_messages(host, session_id, verbose)
    results["tests"].append(messages_result)
    
    if not messages_result["passed"]:
        results["success"] = False
    
    return results


def test_create_session(host, verbose=False):
    """Test the session creation endpoint"""
    
    endpoint = f"{host}/api/sessions"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(endpoint)
            
            if verbose:
                print(f"Request: POST {endpoint}")
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("session_id"):
                    return {
                        "name": "Create session",
                        "endpoint": endpoint,
                        "passed": True,
                        "status_code": response.status_code,
                        "data": data
                    }
            
            print(f"Attempt {attempt + 1} failed. Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
            
        except requests.RequestException as e:
            print(f"Request error: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
    
    return {
        "name": "Create session",
        "endpoint": endpoint,
        "passed": False,
        "error": "Failed to create a new session after multiple attempts"
    }


def test_send_message(host, session_id, verbose=False):
    """Test the send message endpoint"""
    
    endpoint = f"{host}/api/sessions/{session_id}/messages"
    payload = {
        "message": "Hello, I'm looking for drought-resistant plants for my garden in Las Vegas."
    }
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if verbose:
                print(f"Request: POST {endpoint}")
                print(f"Request body: {json.dumps(payload)}")
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("response"):
                    return {
                        "name": "Send message",
                        "endpoint": endpoint,
                        "passed": True,
                        "status_code": response.status_code,
                        "data": data
                    }
            
            print(f"Attempt {attempt + 1} failed. Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
            
        except requests.RequestException as e:
            print(f"Request error: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
    
    return {
        "name": "Send message",
        "endpoint": endpoint,
        "passed": False,
        "error": "Failed to send message after multiple attempts"
    }


def test_get_messages(host, session_id, verbose=False):
    """Test the get messages endpoint"""
    
    endpoint = f"{host}/api/sessions/{session_id}/messages"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(endpoint)
            
            if verbose:
                print(f"Request: GET {endpoint}")
                print(f"Response status: {response.status_code}")
                print(f"Response body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "messages" in data:
                    return {
                        "name": "Get messages",
                        "endpoint": endpoint,
                        "passed": True,
                        "status_code": response.status_code,
                        "data": data
                    }
            
            print(f"Attempt {attempt + 1} failed. Retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
            
        except requests.RequestException as e:
            print(f"Request error: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
    
    return {
        "name": "Get messages",
        "endpoint": endpoint,
        "passed": False,
        "error": "Failed to get messages after multiple attempts"
    }


def run_interactive_test(host=DEFAULT_HOST):
    """Run an interactive test session with the agent"""
    
    print("Starting interactive test session...")
    
    # Create a session
    session_result = test_create_session(host, verbose=False)
    if not session_result["passed"]:
        print("❌ Failed to create a session.")
        return
    
    session_id = session_result["data"]["session_id"]
    print(f"✅ Session created: {session_id}")
    
    print("\nYou can now chat with the customer service agent.")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        # Get user input
        user_message = input("\nYou: ")
        
        if user_message.lower() in ["exit", "quit", "bye"]:
            print("Ending test session. Goodbye!")
            break
        
        # Send message to agent
        endpoint = f"{host}/api/sessions/{session_id}/messages"
        payload = {"message": user_message}
        
        try:
            print("Sending message to agent...")
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("response"):
                    print(f"\nAgent: {data['response']}")
                else:
                    print("❌ Error in agent response.")
            else:
                print(f"❌ Request failed with status code {response.status_code}")
                
        except requests.RequestException as e:
            print(f"❌ Request error: {e}")


def main():
    """Main function to parse arguments and run tests"""
    
    parser = argparse.ArgumentParser(description="Test the Customer Service Agent Web App API")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host URL (default: {DEFAULT_HOST})")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive_test(args.host)
    else:
        print(f"Testing API endpoints at {args.host}...")
        results = test_api_endpoints(args.host, args.verbose)
        
        # Print results summary
        print("\n=== Test Results ===")
        
        if results["success"]:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
        
        for test in results["tests"]:
            status = "✅" if test["passed"] else "❌"
            print(f"{status} {test['name']}")
            
            if not test["passed"] and "error" in test:
                print(f"   Error: {test['error']}")
        
        print("\nDetailed results:")
        print(json.dumps(results, indent=2))
        
        # Return exit code based on success
        sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()