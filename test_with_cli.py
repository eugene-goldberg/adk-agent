#!/usr/bin/env python3
"""
Script to test communication with the deployed agents using a command-line approach.
"""

import os
import sys
import subprocess
import json
from dotenv import load_dotenv

def list_deployments_with_cli():
    """List deployments using the CLI tool."""
    print("Listing deployments using the CLI...")
    try:
        result = subprocess.run(
            ["python3", "deployment/customer_service_remote.py", "--list"],
            env={**os.environ, "PYTHONPATH": os.getcwd()},
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error listing deployments: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return None

def create_session_with_cli(resource_id, user_id="test_user"):
    """Create a session using the CLI tool."""
    print(f"Creating session for {resource_id}...")
    try:
        result = subprocess.run(
            [
                "python3", 
                "deployment/customer_service_remote.py", 
                "--create_session", 
                f"--resource_id={resource_id}", 
                f"--user_id={user_id}"
            ],
            env={**os.environ, "PYTHONPATH": os.getcwd()},
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
        # Extract session ID from output
        for line in result.stdout.splitlines():
            if "Session ID:" in line:
                session_id = line.split("Session ID:")[1].strip()
                return session_id
        
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error creating session: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return None

def send_message_with_cli(resource_id, user_id, session_id, message):
    """Send a message using the CLI tool."""
    print(f"Sending message to {resource_id}, session {session_id}...")
    print(f"Message: {message}")
    
    try:
        result = subprocess.run(
            [
                "python3", 
                "deployment/customer_service_remote.py", 
                "--send", 
                f"--resource_id={resource_id}", 
                f"--user_id={user_id}", 
                f"--session_id={session_id}",
                f"--message={message}"
            ],
            env={**os.environ, "PYTHONPATH": os.getcwd()},
            check=True,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error sending message: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("Command timed out after 2 minutes")
        return False

def extract_resource_ids(output):
    """Extract resource IDs from the CLI output."""
    resource_ids = []
    if not output:
        return resource_ids
    
    for line in output.splitlines():
        if line.startswith("- "):
            parts = line.strip("- ").split(": ")
            if len(parts) == 2:
                display_name, resource_id = parts
                resource_ids.append({"display_name": display_name, "resource_id": resource_id})
            elif len(parts) == 1 and "projects/" in parts[0]:
                resource_ids.append({"display_name": "Unknown", "resource_id": parts[0]})
    
    return resource_ids

def main():
    """Main function."""
    load_dotenv()
    
    print("Starting communication test with deployed agents using CLI tools...")
    output = list_deployments_with_cli()
    
    if not output:
        print("Failed to list deployments. Exiting.")
        return
    
    resource_ids = extract_resource_ids(output)
    if not resource_ids:
        print("No deployments found in the output. Exiting.")
        return
    
    for deployment in resource_ids:
        display_name = deployment["display_name"]
        resource_id = deployment["resource_id"]
        
        print(f"\n==== Testing {display_name} ====")
        
        # Create a session
        user_id = "test_user"
        session_id = create_session_with_cli(resource_id, user_id)
        
        if not session_id:
            print(f"Failed to create session for {display_name}. Skipping.")
            continue
        
        # Test with a simple message
        test_message_text = "Hello! How can you help me today?"
        success = send_message_with_cli(resource_id, user_id, session_id, test_message_text)
        
        if success:
            print(f"\n✅ Successfully communicated with {display_name}")
        else:
            print(f"\n❌ Failed to communicate with {display_name}")

if __name__ == "__main__":
    main()