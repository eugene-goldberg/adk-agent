#!/usr/bin/env python3
"""
Direct Chat with Vertex AI Agent

This script connects directly to a deployed Vertex AI agent using the Google Cloud API.
It creates a session and allows for interactive communication with the agent.
"""

import os
import uuid
import json
import time
import sys
from dotenv import load_dotenv
import colorama
from colorama import Fore, Style
import requests
import google.auth
import google.auth.transport.requests

# Initialize colorama for colored terminal output
colorama.init()

# Load environment variables from .env file
load_dotenv()

# Define message printing functions
def print_system_message(message):
    """Print a system message with formatting"""
    print(f"{Fore.YELLOW}System: {Style.RESET_ALL}{message}")

def print_agent_message(message):
    """Print a message from the agent with formatting"""
    print(f"{Fore.BLUE}Agent: {Style.RESET_ALL}{message}")

def print_user_message(message):
    """Print a user message with formatting"""
    print(f"{Fore.GREEN}You: {Style.RESET_ALL}{message}")

def print_error_message(message):
    """Print an error message with formatting"""
    print(f"{Fore.RED}Error: {Style.RESET_ALL}{message}")

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
RESOURCE_ID = os.getenv("AGENT_RESOURCE_ID", "1818126039411326976")

# Use full resource path format
FULL_RESOURCE_PATH = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{RESOURCE_ID}"
API_ENDPOINT = f"https://{LOCATION}-aiplatform.googleapis.com/v1/{FULL_RESOURCE_PATH}"

def get_access_token():
    """Get access token using application default credentials."""
    try:
        credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        print_system_message(f"Successfully obtained access token for project: {project}")
        return credentials.token
    except Exception as e:
        print_error_message(f"Error getting access token: {e}")
        return None

def create_session():
    """Create a new session with the Vertex AI agent."""
    session_id = str(uuid.uuid4())
    user_id = f"user_{str(uuid.uuid4())[:8]}"
    
    url = f"{API_ENDPOINT}:create_session"
    
    token = get_access_token()
    if token is None:
        print_error_message("Failed to get access token. Make sure you're authenticated with gcloud.")
        sys.exit(1)
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "user_id": user_id,
        "session_id": session_id
    }
    
    try:
        print_system_message(f"Creating session for user {user_id}...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print_system_message(f"Session created successfully with ID: {session_id}")
            return {"user_id": user_id, "session_id": session_id}
        else:
            print_error_message(f"Error creating session: {response.status_code}")
            if response.text:
                print_error_message(f"Response: {response.text}")
            sys.exit(1)
    except Exception as e:
        print_error_message(f"Exception during session creation: {e}")
        sys.exit(1)

def send_message(session_info, message):
    """Send a message to the agent and get a response."""
    session_id = session_info["session_id"]
    user_id = session_info["user_id"]
    
    url = f"{API_ENDPOINT}:stream_query"
    
    token = get_access_token()
    if token is None:
        print_error_message("Failed to get access token.")
        return "Error: Authentication failed"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "user_id": user_id,
        "session_id": session_id,
        "message": message
    }
    
    try:
        print_system_message("Sending message to agent...")
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            try:
                data = response.json()
                return data.get("text", "Sorry, I couldn't process your request.")
            except ValueError:
                # For streaming responses, read the response text directly
                return response.text if response.text else "Sorry, I couldn't process your request."
        else:
            print_error_message(f"Error sending message: {response.status_code}")
            if response.text:
                print_error_message(f"Response: {response.text}")
            return "Sorry, there was an error communicating with the agent."
    except Exception as e:
        print_error_message(f"Exception during message sending: {e}")
        return "Sorry, an error occurred while communicating with the agent."

def run_chat():
    """Run an interactive chat session with the agent."""
    print_system_message("Starting direct chat with Cymbal Home & Garden Customer Service Agent")
    print_system_message(f"Project: {PROJECT_ID}, Location: {LOCATION}, Resource ID: {RESOURCE_ID}")
    print_system_message(f"API Endpoint: {API_ENDPOINT}")
    
    # Create a session
    session_info = create_session()
    print_system_message(f"Created session with ID: {session_info['session_id']} for user: {session_info['user_id']}")
    
    # Display welcome message
    print_agent_message("Welcome to Cymbal Home & Garden! I'm your customer service assistant. How can I help you today?")
    
    while True:
        # Get user input
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print_agent_message("Thank you for chatting with Cymbal Home & Garden. Have a great day!")
            break
        
        # Simulate typing
        print_system_message("Agent is thinking...")
        
        # Get response from agent
        response = send_message(session_info, user_input)
        
        # Display agent response
        print_agent_message(response)

if __name__ == "__main__":
    run_chat()