#!/usr/bin/env python3
"""
Test Vertex AI ReasoningEngine using REST API

This script tests the interaction with a deployed Vertex AI ReasoningEngine
using direct REST API calls.
"""

import os
import uuid
import json
import sys
from dotenv import load_dotenv
import requests
import google.auth
import google.auth.transport.requests

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
RESOURCE_ID = os.getenv("AGENT_RESOURCE_ID", "1818126039411326976")

# URL components
BASE_URL = f"https://{LOCATION}-aiplatform.googleapis.com/v1"
RESOURCE_PATH = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
API_ENDPOINT = f"{BASE_URL}/{RESOURCE_PATH}"

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

def test_get_resource():
    """Test GET request to fetch the resource information."""
    token = get_access_token()
    if token is None:
        print("Failed to get access token")
        return False
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    url = API_ENDPOINT
    print(f"Requesting resource info from: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Resource name: {data.get('name')}")
            print(f"Display name: {data.get('displayName')}")
            print(f"Description: {data.get('description')}")
            
            # List available methods
            print("\nAvailable methods:")
            for method in data.get('spec', {}).get('classMethods', []):
                print(f"- {method.get('name')}: {method.get('api_mode')}")
                
            return True
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_method_execution():
    """Test each method available on the reasoning engine."""
    token = get_access_token()
    if token is None:
        print("Failed to get access token")
        return False
        
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # We'll test each method separately
    methods_to_test = [
        {
            "name": "create_session",
            "payload": {
                "user_id": f"user_{str(uuid.uuid4())[:8]}"
            }
        },
        {
            "name": "list_sessions",
            "payload": {
                "user_id": f"user_{str(uuid.uuid4())[:8]}"
            }
        },
        {
            "name": "stream_query",
            "payload": {
                "user_id": f"user_{str(uuid.uuid4())[:8]}",
                "message": "Hello, I need help with my garden."
            }
        }
    ]
    
    for method in methods_to_test:
        method_name = method["name"]
        payload = method["payload"]
        
        url = f"{API_ENDPOINT}:{method_name}"
        print(f"\nTesting method: {method_name}")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                print("Response:")
                if response.text:
                    try:
                        formatted_json = json.dumps(response.json(), indent=2)
                        print(formatted_json)
                    except:
                        print(response.text[:1000] + "..." if len(response.text) > 1000 else response.text)
                else:
                    print("Empty response")
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    print("Testing Vertex AI ReasoningEngine API")
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print(f"Resource ID: {RESOURCE_ID}")
    print(f"API Endpoint: {API_ENDPOINT}")
    print("-" * 80)
    
    if test_get_resource():
        print("\nResource info retrieved successfully! Testing method execution...")
        test_method_execution()
    else:
        print("\nFailed to retrieve resource info. Check your configuration and permissions.")