#!/usr/bin/env python3
"""
Simple chat client for interacting with the Customer Service Agent using ADK.

This script provides a simple terminal interface for chatting with the 
Customer Service Agent locally using the ADK framework.
"""

import os
import asyncio
import argparse
from dotenv import load_dotenv
import colorama
from colorama import Fore, Style

# Import ADK components - ensure PYTHONPATH is set correctly
try:
    from google.adk import Agent
    from google.adk.sessions import Session
    from customer_service.agent import root_agent
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you have set PYTHONPATH correctly and activated the virtual environment.")
    print("Try: source .venv-py312/bin/activate && export PYTHONPATH=$PYTHONPATH:$(pwd)")
    exit(1)

# Initialize colorama for colored text output
colorama.init()

def print_system_message(message):
    """Print a system message with formatting"""
    print(f"{Fore.YELLOW}System: {Style.RESET_ALL}{message}")

def print_agent_message(message):
    """Print a message from the agent with formatting"""
    print(f"{Fore.BLUE}Agent: {Style.RESET_ALL}{message}")

def print_user_message(message):
    """Print a user message with formatting"""
    print(f"{Fore.GREEN}You: {Style.RESET_ALL}{message}")

async def chat_session(agent: Agent):
    """Run an interactive chat session with the specified agent."""
    print_system_message("Starting chat with Cymbal Home & Garden Customer Service Agent")
    print_system_message("Type 'exit' to quit the chat session")
    
    # Create a session
    session = Session(agent=agent, user_id="test_user")
    print_system_message(f"Session created: {session.id}")
    
    # Initial welcome message
    print_agent_message("Welcome to Cymbal Home & Garden! I'm your customer service assistant. How can I help you today?")
    
    # Chat loop
    while True:
        # Get user input
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print_agent_message("Thank you for chatting with Cymbal Home & Garden. Have a great day!")
            break
        
        try:
            # Send message to agent
            print_system_message("Processing your message...")
            response = await session.send_message(user_input)
            
            # Print agent response
            if response:
                print_agent_message(response.text)
            else:
                print_system_message("No response received from agent")
        except Exception as e:
            print_system_message(f"Error: {e}")

def main():
    """Main entry point for the chat client."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Chat with the Customer Service Agent using ADK")
    args = parser.parse_args()
    
    try:
        # Run the chat session
        asyncio.run(chat_session(root_agent))
    except KeyboardInterrupt:
        print_system_message("\nChat session terminated by user")
    except Exception as e:
        print_system_message(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()