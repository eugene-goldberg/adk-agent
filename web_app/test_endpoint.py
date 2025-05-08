#!/usr/bin/env python3
"""
Simple script to test the agent API endpoints directly
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_discover_endpoint():
    """Test the agent discovery endpoint"""
    print("Testing agent discovery endpoint...")
    response = requests.get(f"{BASE_URL}/api/agent/discover")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        return response.json().get("agents", [])
    return []

if __name__ == "__main__":
    agents = test_discover_endpoint()
    if agents:
        print(f"Found {len(agents)} agents:")
        for agent in agents:
            print(f"- {agent.get('display_name', 'Unknown')}: {agent.get('id', 'Unknown')}")
    else:
        print("No agents found or error accessing the endpoint")
        sys.exit(1)
    
    sys.exit(0)