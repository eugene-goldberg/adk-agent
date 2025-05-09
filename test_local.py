#!/usr/bin/env python3
"""
Script to test the customer service agent locally with an interactive interface.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv
import time
import colorama
from colorama import Fore, Style

# Initialize colorama
colorama.init()

def print_info(message):
    """Print an info message with formatting"""
    print(f"{Fore.CYAN}INFO: {Style.RESET_ALL}{message}")

def print_error(message):
    """Print an error message with formatting"""
    print(f"{Fore.RED}ERROR: {Style.RESET_ALL}{message}")

def create_session():
    """Create a local session with the customer service agent"""
    print_info("Creating a new local session...")
    
    try:
        result = subprocess.run(
            ["python", "deployment/customer_service_local.py", "--create_session"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract session ID from the output
        output_lines = result.stdout.splitlines()
        session_id = None
        
        for line in output_lines:
            if "Session ID:" in line:
                session_id = line.split("Session ID:")[1].strip()
                break
        
        if not session_id:
            print_error("Failed to extract session ID from output")
            print(result.stdout)
            return None
        
        print_info(f"Session created successfully with ID: {session_id}")
        return session_id
    
    except subprocess.CalledProcessError as e:
        print_error(f"Error creating session: {e}")
        print(e.stderr)
        return None

def send_message(session_id, message):
    """Send a message to the agent and return the response"""
    print_info(f"Sending message: {message}")
    
    try:
        result = subprocess.run(
            ["python", "deployment/customer_service_local.py", "--send", 
             f"--session_id={session_id}", f"--message={message}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Extract agent response from output
        output = result.stdout
        if "Response:" in output:
            response_section = output.split("Response:")[1].strip()
            
            # Skip any log lines that might appear in the output
            response_lines = []
            for line in response_section.splitlines():
                if not line.startswith("INFO:") and not line.startswith("DEBUG:"):
                    response_lines.append(line)
            
            response = "\n".join(response_lines).strip()
            return response
        else:
            print_error("Failed to extract response from output")
            print(output)
            return "ERROR: Failed to parse agent response"
    
    except subprocess.CalledProcessError as e:
        print_error(f"Error sending message: {e}")
        print(e.stderr)
        return f"ERROR: {e}"

def run_interactive_test():
    """Run an interactive test with the customer service agent"""
    print_info("Starting interactive test with Customer Service Agent")
    
    # Set up environment
    load_dotenv()
    os.environ["PYTHONPATH"] = f"{os.getcwd()}:{os.environ.get('PYTHONPATH', '')}"
    
    # Create a session
    session_id = create_session()
    if not session_id:
        print_error("Failed to create session. Exiting.")
        return
    
    # Welcome message
    print("\n" + "="*80)
    print(f"{Fore.GREEN}CUSTOMER SERVICE AGENT CHAT{Style.RESET_ALL}")
    print("Type your messages below. Enter 'exit' to end the chat.")
    print("="*80 + "\n")
    
    # Chat loop
    while True:
        # Get user input
        user_input = input(f"{Fore.YELLOW}You: {Style.RESET_ALL}")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print_info("Ending chat session...")
            break
        
        # Send message to agent
        response = send_message(session_id, user_input)
        
        # Display agent response
        print(f"{Fore.BLUE}Agent: {Style.RESET_ALL}{response}\n")

if __name__ == "__main__":
    run_interactive_test()