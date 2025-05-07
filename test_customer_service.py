#!/usr/bin/env python3
"""
Test script for the Customer Service Agent.

This script provides both instructions and interactive testing functionality
for the Customer Service Agent.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the Customer Service Agent")
    parser.add_argument("--mode", choices=["local", "remote"], default="local",
                        help="Mode to run in (local or remote)")
    parser.add_argument("--resource_id", help="Resource ID for remote mode")
    parser.add_argument("--session_id", help="Session ID for testing")
    parser.add_argument("--interactive", action="store_true", 
                        help="Run in interactive mode")
    return parser.parse_args()

def show_instructions():
    """Show instructions for testing the Customer Service Agent."""
    print("# Testing the Customer Service Agent")
    print("\nTo test the Customer Service Agent locally, you can use the Google ADK CLI.")
    print("Make sure you have the ADK CLI installed and configured:")
    print("\n```bash")
    print("pip install google-adk")
    print("```")
    
    print("\n## Local Testing")
    print("1. Using ADK CLI:")
    print("```bash")
    print("cd /Users/eugene/dev/ai/agents/deploy-adk-agent-engine")
    print("export PYTHONPATH=$PYTHONPATH:$(pwd)")
    print("adk run customer_service")
    print("```")
    
    print("2. Using the deployment script:")
    print("```bash")
    print("python deployment/customer_service_local.py --create_session")
    print("python deployment/customer_service_local.py --send --session_id=YOUR_SESSION_ID --message=\"Hello, I need help with a product.\"")
    print("```")
    
    print("3. Using this script's interactive mode:")
    print("```bash")
    print("python test_customer_service.py --mode=local --session_id=YOUR_SESSION_ID --interactive")
    print("```")
    
    print("\n## Remote Testing")
    print("1. List available deployments:")
    print("```bash")
    print("python deployment/customer_service_remote.py --list")
    print("```")
    
    print("2. Create a session:")
    print("```bash")
    print("python deployment/customer_service_remote.py --create_session --resource_id=YOUR_RESOURCE_ID")
    print("```")
    
    print("3. Send messages to the agent:")
    print("```bash")
    print("python deployment/customer_service_remote.py --send --resource_id=YOUR_RESOURCE_ID --session_id=YOUR_SESSION_ID --message=\"Hello, I need help with a product.\"")
    print("```")
    
    print("4. Using this script's interactive mode:")
    print("```bash")
    print("python test_customer_service.py --mode=remote --resource_id=YOUR_RESOURCE_ID --session_id=YOUR_SESSION_ID --interactive")
    print("```")
    
    print("\n## Sample Test Messages")
    print("Here are some sample messages you can use to test the Customer Service Agent:")
    
    print("\n### Product Recommendations")
    print("- \"I'm looking for a lawnmower recommendation.\"")
    print("- \"What gardening tools would you recommend for a beginner?\"")
    print("- \"I need a new irrigation system for my garden.\"")
    
    print("\n### Order Management")
    print("- \"I want to check the status of my recent order.\"")
    print("- \"I'd like to add a garden hose to my cart.\"")
    print("- \"What's in my shopping cart right now?\"")
    
    print("\n### Service Scheduling")
    print("- \"I need to schedule a consultation for my landscaping project.\"")
    print("- \"When are your gardening experts available for a consultation?\"")
    print("- \"I'd like to book a lawn assessment.\"")
    
    print("\n### General Customer Service")
    print("- \"What's your return policy?\"")
    print("- \"How do I care for my new rosebush?\"")
    print("- \"Do you offer any gardening classes or workshops?\"")

def interactive_local_mode(session_id):
    """Run the agent in interactive local mode."""
    if not session_id:
        print("Error: Session ID is required for interactive mode.")
        print("Create a session first with: python deployment/customer_service_local.py --create_session")
        sys.exit(1)
    
    print("\nInteractive Local Mode")
    print("Enter your messages below. Type 'exit' to quit.")
    
    while True:
        message = input("\nYou: ")
        if message.lower() == "exit":
            break
        
        cmd = f"python deployment/customer_service_local.py --send --session_id={session_id} --message=\"{message}\""
        os.system(cmd)

def interactive_remote_mode(resource_id, session_id):
    """Run the agent in interactive remote mode."""
    if not resource_id or not session_id:
        print("Error: Resource ID and Session ID are required for interactive mode.")
        print("List available deployments: python deployment/customer_service_remote.py --list")
        print("Create a session: python deployment/customer_service_remote.py --create_session --resource_id=YOUR_RESOURCE_ID")
        sys.exit(1)
    
    print("\nInteractive Remote Mode")
    print("Enter your messages below. Type 'exit' to quit.")
    
    while True:
        message = input("\nYou: ")
        if message.lower() == "exit":
            break
        
        cmd = f"python deployment/customer_service_remote.py --send --resource_id={resource_id} --session_id={session_id} --message=\"{message}\""
        os.system(cmd)

def main():
    """Main function."""
    load_dotenv()
    args = parse_arguments()
    
    if args.interactive:
        if args.mode == "local":
            interactive_local_mode(args.session_id)
        else:
            interactive_remote_mode(args.resource_id, args.session_id)
    else:
        show_instructions()

if __name__ == "__main__":
    main()