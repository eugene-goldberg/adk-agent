#!/usr/bin/env python3
"""List all sessions for the specified agent."""

import os
import sys
import argparse
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines
import json
from pprint import pprint

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="List all sessions for a deployed agent")
    parser.add_argument("--resource_id", help="Resource ID of the deployed agent", required=True)
    parser.add_argument("--user_id", default="test_user", help="User ID for sessions")
    return parser.parse_args()

def main():
    """Main function."""
    load_dotenv()
    args = parse_arguments()
    
    # Load environment variables
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    
    if not project_id:
        print("Missing required environment variable: GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("Missing required environment variable: GOOGLE_CLOUD_LOCATION")
        return
    
    # Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    
    # Get the deployed app
    try:
        remote_app = agent_engines.get(args.resource_id)
        print(f"Successfully retrieved agent: {remote_app.resource_name}")
        
        # List all sessions
        try:
            sessions = remote_app.list_sessions(user_id=args.user_id)
            print(f"\nSessions for user '{args.user_id}':")
            
            if not sessions:
                print("No sessions found.")
                return
            
            print(f"Raw sessions response: {sessions}")
            
            # Try to parse differently
            if isinstance(sessions, dict) and 'sessions' in sessions:
                sessions_list = sessions['sessions']
                for session in sessions_list:
                    print(f"- Session ID: {session.get('id', 'Unknown')}")
            elif isinstance(sessions, list):
                for session in sessions:
                    if isinstance(session, dict):
                        print(f"- Session ID: {session.get('id', 'Unknown')}")
                    else:
                        print(f"- Session: {session}")
            else:
                print(f"Unable to parse sessions. Type: {type(sessions)}")
                
        except Exception as e:
            print(f"Error listing sessions: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"Error retrieving agent: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()