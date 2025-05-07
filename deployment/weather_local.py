"""
Local deployment script for the Weather Agent.
"""

import os
import sys
import argparse

import vertexai
from dotenv import load_dotenv
from vertexai.preview import reasoning_engines

from weather_agent.agent import weather_agent


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Deploy and test the Weather Agent locally")
    
    # Create mutually exclusive group for operations
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create_session", action="store_true", help="Create a new session")
    group.add_argument("--list_sessions", action="store_true", help="List all sessions")
    group.add_argument("--get_session", action="store_true", help="Get a specific session")
    group.add_argument("--send", action="store_true", help="Send a message to a session")
    
    # Additional parameters
    parser.add_argument("--user_id", default="test_user", help="User ID for session operations")
    parser.add_argument("--session_id", help="Session ID for operations")
    parser.add_argument("--message", help="Message to send")
    
    return parser.parse_args()


def main():
    """Main function to run the local deployment."""
    args = parse_arguments()
    
    # Load environment variables
    load_dotenv()

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")

    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        sys.exit(1)
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        sys.exit(1)

    # Initialize Vertex AI
    print(f"Initializing Vertex AI with project={project_id}, location={location}")
    vertexai.init(
        project=project_id,
        location=location,
    )

    # Check if OpenWeatherMap API key is available
    openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    if not openweathermap_api_key:
        print("Warning: OPENWEATHERMAP_API_KEY environment variable is not set.")
        print("The weather agent will not be able to fetch real weather data.")
        print("Please get an API key from https://openweathermap.org/ and set it in your .env file.")
    else:
        print("OpenWeatherMap API key found.")
        
    # Create the app
    print("Creating local app instance...")
    app = reasoning_engines.AdkApp(
        agent=weather_agent,
        enable_tracing=True,
    )

    # Handle operations based on arguments
    if args.create_session:
        # Create a session
        print(f"Creating session for user '{args.user_id}'...")
        session = app.create_session(user_id=args.user_id)
        print("Session created:")
        print(f"  Session ID: {session.id}")
        print(f"  User ID: {session.user_id}")
        print(f"  App name: {session.app_name}")
    
    elif args.list_sessions:
        # List sessions
        print(f"Listing sessions for user '{args.user_id}'...")
        sessions = app.list_sessions(user_id=args.user_id)
        if hasattr(sessions, "sessions"):
            print(f"Found sessions: {sessions.sessions}")
        elif hasattr(sessions, "session_ids"):
            print(f"Found session IDs: {sessions.session_ids}")
        else:
            print(f"Sessions response: {sessions}")
    
    elif args.get_session:
        # Get a specific session
        if not args.session_id:
            print("Error: --session_id is required for --get_session")
            sys.exit(1)
        
        print(f"Getting session {args.session_id} for user '{args.user_id}'...")
        session = app.get_session(user_id=args.user_id, session_id=args.session_id)
        print("Session details:")
        print(f"  ID: {session.id}")
        print(f"  User ID: {session.user_id}")
        print(f"  App name: {session.app_name}")
    
    elif args.send:
        # Send a message
        if not args.session_id:
            print("Error: --session_id is required for --send")
            sys.exit(1)
        if not args.message:
            print("Error: --message is required for --send")
            sys.exit(1)
        
        print(f"Sending message to session {args.session_id}:")
        print(f"Message: {args.message}")
        print("\nResponse:")
        for event in app.stream_query(
            user_id=args.user_id,
            session_id=args.session_id,
            message=args.message,
        ):
            print(event)


if __name__ == "__main__":
    main()