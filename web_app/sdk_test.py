#!/usr/bin/env python3
"""
Test Vertex AI ReasoningEngine using Google Cloud SDK

This script uses the Google Cloud SDK to interact with a deployed Vertex AI ReasoningEngine.
"""

import os
import uuid
from google.cloud import aiplatform
from dotenv import load_dotenv
import google.auth

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "pickuptruckapp")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
RESOURCE_ID = os.getenv("AGENT_RESOURCE_ID", "1818126039411326976")

def init_api():
    """Initialize the AI Platform API client."""
    # We need to explicitly authenticate using ADC
    credentials, project = google.auth.default()
    
    # Initialize the SDK
    aiplatform.init(
        project=PROJECT_ID,
        location=LOCATION,
        credentials=credentials
    )
    
    return True

def test_reasoning_engine():
    """Test the deployed reasoning engine."""
    print(f"Testing ReasoningEngine with ID: {RESOURCE_ID}")
    
    try:
        # Get the ReasoningEngine instance
        reasoning_engine = aiplatform.ReasoningEngine(reasoning_engine_id=RESOURCE_ID)
        print(f"Successfully retrieved ReasoningEngine: {reasoning_engine.display_name}")
        
        # List available methods
        print("Available methods:")
        for method in reasoning_engine.class_methods:
            print(f"- {method.name}")
            
        return reasoning_engine
    except Exception as e:
        print(f"Error accessing ReasoningEngine: {e}")
        return None

def run_chat_test(reasoning_engine):
    """Run a simple chat test with the reasoning engine."""
    if reasoning_engine is None:
        print("Cannot run chat test: ReasoningEngine is not available")
        return
    
    try:
        # Create a user ID
        user_id = f"user_{str(uuid.uuid4())[:8]}"
        print(f"Creating session for user: {user_id}")
        
        # Create a session
        response = reasoning_engine.create_session(user_id=user_id)
        session_id = response.get("session_id")
        if not session_id:
            print("Failed to create session: No session ID returned")
            return
            
        print(f"Session created with ID: {session_id}")
        
        # Send a test message
        messages = [
            "Hello, I need help with my garden.",
            "What plants are good for a sunny spot?",
            "Thank you for the information!"
        ]
        
        for msg in messages:
            print(f"\nSending message: '{msg}'")
            response = reasoning_engine.stream_query(
                user_id=user_id,
                session_id=session_id,
                message=msg
            )
            print(f"Response: {response}")
            
    except Exception as e:
        print(f"Error during chat test: {e}")

if __name__ == "__main__":
    if init_api():
        engine = test_reasoning_engine()
        if engine:
            run_chat_test(engine)
    else:
        print("Failed to initialize API")