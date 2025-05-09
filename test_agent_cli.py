#!/usr/bin/env python3
"""
Command-line script for testing the Customer Service Agent with minimal dependencies.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from colorama import Fore, Style, init

# Initialize colorama
init()

# Set constants
PROJECT_ID = "pickuptruckapp"
REGION = "us-central1"
# Default agent ID, but will be discovered dynamically when possible
DEFAULT_AGENT_ID = "1818126039411326976"

# Agent info will be populated dynamically during discovery
discovered_agents = []

# Set the proper Python path for imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def run_command(command):
    """Run a shell command with proper environment variables."""
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{PROJECT_ROOT}:{env.get('PYTHONPATH', '')}"
    
    try:
        print(f"Executing: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            env=env
        )
        
        if result.stdout:
            print(f"STDOUT: {result.stdout[:200]}{'...' if len(result.stdout) > 200 else ''}")
        if result.stderr:
            print(f"STDERR: {result.stderr[:200]}{'...' if len(result.stderr) > 200 else ''}")
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except Exception as e:
        print(f"Error executing command: {e}")
        return {
            "success": False,
            "error": str(e),
            "returncode": -1
        }


def extract_session_id(output):
    """Extract session ID from command output."""
    if not output:
        return None
    match = re.search(r'Session ID: (\d+)', output)
    if match:
        return match.group(1)
    return None


def extract_text_response(output):
    """Extract the text response from the agent output."""
    responses = []
    
    try:
        # First try to find JSON objects with 'content' key
        content_matches = re.findall(r"{'content': {'parts': \[{'text': \"([^']+)\"}]", output)
        if content_matches:
            for match in content_matches:
                cleaned_text = match.replace('\\n', '\n').replace('\\\"', '"')
                responses.append(cleaned_text)
            return "\n".join(responses)
            
        # Second approach - look for parts with text
        pattern = re.compile(r"'text': \"(.*?)\"", re.DOTALL)
        text_matches = pattern.findall(output)
        if text_matches:
            for match in text_matches:
                cleaned_text = match.replace('\\n', '\n').replace('\\\"', '"')
                responses.append(cleaned_text)
            return "\n".join(responses)
        
        # If we get here, we didn't find any text in the expected format
        # Just return the raw output for debugging
        return f"[Could not parse response - raw output excerpt: {output[:500]}...]"
    except Exception as e:
        return f"[Error parsing response: {e} - raw output excerpt: {output[:200]}...]"


def discover_agents():
    """Discover agents deployed in Vertex AI."""
    print("\n=== DISCOVERING AGENTS ===\n")
    
    global discovered_agents
    discovered_agents = []
    
    result = run_command(f"./list_agents.sh --project {PROJECT_ID}")
    
    if not result["success"]:
        print(f"Error discovering agents: {result['stderr']}")
        # Fall back to default agent ID if discovery fails
        agent_info = {
            "id": DEFAULT_AGENT_ID,
            "resource_id": f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{DEFAULT_AGENT_ID}",
            "display_name": "Customer Service Agent (Default)",
            "is_default": True
        }
        discovered_agents.append(agent_info)
        return agent_info
    
    # Parse the output to extract agent information
    output = result["stdout"]
    agent_blocks = re.split(r'ID:', output)[1:]  # Split by ID: marker
    
    for block in agent_blocks:
        try:
            agent_id = block.strip().split('\n')[0].strip()
            
            # Extract other information using regex
            display_name_match = re.search(r'Display Name: (.+)', block)
            description_match = re.search(r'Description: (.+)', block)
            
            agent_info = {
                "id": agent_id,
                "resource_id": f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{agent_id}",
                "display_name": display_name_match.group(1) if display_name_match else f"Agent {agent_id}",
                "description": description_match.group(1) if description_match else "No description",
                "is_default": False
            }
            
            discovered_agents.append(agent_info)
            print(f"Found agent: {agent_info['display_name']} (ID: {agent_id})")
        except Exception as e:
            print(f"Error parsing agent block: {e}")
    
    if not discovered_agents:
        print("No agents found. Using default agent ID.")
        agent_info = {
            "id": DEFAULT_AGENT_ID,
            "resource_id": f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{DEFAULT_AGENT_ID}",
            "display_name": "Customer Service Agent (Default)",
            "is_default": True
        }
        discovered_agents.append(agent_info)
        return agent_info
    
    # Select the first agent or agent with "customer" in the name as default
    selected_agent = None
    for agent in discovered_agents:
        if "customer" in agent["display_name"].lower():
            selected_agent = agent
            break
    
    # If no customer service agent found, use the first one
    if not selected_agent and discovered_agents:
        selected_agent = discovered_agents[0]
    
    print(f"\nSelected agent: {selected_agent['display_name']} (ID: {selected_agent['id']})")
    return selected_agent


def create_session(resource_id=None):
    """Create a session with a Vertex AI agent."""
    print("\n=== CREATING SESSION ===\n")
    
    if not resource_id:
        # Build a default resource ID
        agent_id = DEFAULT_AGENT_ID
        resource_id = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{agent_id}"
    
    command = f"python3 deployment/customer_service_remote.py --create_session --resource_id={resource_id}"
    result = run_command(command)
    
    if not result["success"]:
        print(f"Error creating session: {result['stderr'] or 'Unknown error'}")
        return None
    
    # Extract the session ID from the output
    session_id = extract_session_id(result["stdout"])
    
    if not session_id:
        print("Failed to extract session ID from output")
        print(f"Output: {result['stdout']}")
        return None
    
    print(f"Successfully created session: {session_id}")
    return session_id


def send_message(session_id, message, resource_id=None):
    """Send a message to a Vertex AI agent session."""
    print(f"\n=== SENDING MESSAGE: '{message}' ===\n")
    
    if not resource_id:
        # Build a default resource ID
        agent_id = DEFAULT_AGENT_ID
        resource_id = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{agent_id}"
    
    if not session_id:
        print("Error: Session ID is required")
        return None
    
    if not message:
        print("Error: Message is required")
        return None
    
    command = f'python3 deployment/customer_service_remote.py --send --resource_id={resource_id} --session_id={session_id} --message="{message}"'
    result = run_command(command)
    
    if not result["success"]:
        print(f"Error sending message: {result['stderr'] or 'Unknown error'}")
        return None
    
    # Extract the response from the output
    output = result["stdout"]
    response = extract_text_response(output)
    
    if not response:
        print("No response text found in the output")
        return None
    
    return response


def test_basic_interaction(session_id, resource_id=None):
    """Test basic interaction with the agent."""
    print("\n=== TESTING BASIC INTERACTION ===\n")
    
    message = "Hello, I'm looking for recommendations for plants that would do well in a desert climate."
    response = send_message(session_id, message, resource_id)
    
    if response:
        print("\nResponse from agent:")
        print("==================")
        print(response)
        print("==================")
        return True
    
    return False


def test_weather_integration(session_id, resource_id=None):
    """Test weather integration with the agent."""
    print("\n=== TESTING WEATHER INTEGRATION ===\n")
    
    message = "I'm interested in both flowers and cacti. What's the weather going to be like in Las Vegas this week, and which plants would be suitable based on the forecast?"
    response = send_message(session_id, message, resource_id)
    
    if response:
        print("\nResponse from agent:")
        print("==================")
        print(response)
        print("==================")
        return True
    
    return False


def test_firestore_integration(session_id, resource_id=None):
    """Test Firestore integration with the agent."""
    print("\n=== TESTING FIRESTORE INTEGRATION ===\n")
    
    message = "Could you show me all my bookings in the Firestore database?"
    response = send_message(session_id, message, resource_id)
    
    if response:
        print("\nResponse from agent:")
        print("==================")
        print(response)
        print("==================")
        return True
    
    return False


def run_all_tests(session_id=None, resource_id=None):
    """Run all tests on the agent."""
    print("\n=== RUNNING ALL TESTS ===\n")
    
    # Discover agents and select one if not specified
    selected_agent = None
    if not resource_id:
        selected_agent = discover_agents()
        if not selected_agent:
            print("Failed to discover agents. Aborting tests.")
            return False
        resource_id = selected_agent["resource_id"]
        print(f"Using resource ID: {resource_id}")
    else:
        print(f"Using provided resource ID: {resource_id}")
    
    # Create a session if needed
    if not session_id:
        print("Creating a new session...")
        session_id = create_session(resource_id)
        
        if not session_id:
            print("Failed to create session. Aborting tests.")
            return False
    else:
        print(f"Using existing session ID: {session_id}")
    
    # Run tests
    tests = [
        ("Basic Interaction", test_basic_interaction),
        ("Weather Integration", test_weather_integration),
        ("Firestore Integration", test_firestore_integration)
    ]
    
    results = {}
    
    for name, test_func in tests:
        print(f"\nRunning test: {name}")
        success = test_func(session_id, resource_id)
        results[name] = "Success" if success else "Failed"
        
        # Sleep between tests to avoid rate limiting
        time.sleep(2)
    
    # Print summary
    print("\n=== TEST RESULTS ===\n")
    print(f"Agent: {selected_agent['display_name'] if selected_agent else 'Custom agent'}")
    print(f"Resource ID: {resource_id}")
    print(f"Session ID: {session_id}")
    print("\nTest Results:")
    
    for name, result in results.items():
        status = f"{Fore.GREEN}Success{Fore.RESET}" if result == "Success" else f"{Fore.RED}Failed{Fore.RESET}"
        print(f"- {name}: {status}")
    
    return all(result == "Success" for result in results.values())


def select_agent_interactive():
    """Allow user to select from discovered agents interactively."""
    global discovered_agents
    
    if not discovered_agents:
        # Try to discover agents first
        discover_agents()
    
    if not discovered_agents:
        print("No agents available to select.")
        return None
    
    print("\n=== SELECT AN AGENT ===\n")
    for i, agent in enumerate(discovered_agents, 1):
        print(f"{i}. {agent['display_name']} (ID: {agent['id']})")
    
    while True:
        try:
            choice = input("\nEnter the number of the agent to use (or Enter for default): ")
            
            if not choice.strip():
                # Use the first agent by default
                return discovered_agents[0]
            
            index = int(choice) - 1
            if 0 <= index < len(discovered_agents):
                return discovered_agents[index]
            else:
                print(f"Invalid selection. Please choose 1-{len(discovered_agents)}")
        except ValueError:
            print("Please enter a number.")
        except KeyboardInterrupt:
            print("\nCancelled. Using default agent.")
            return discovered_agents[0]


def save_session_info(resource_id, session_id):
    """Save session info to a file for reuse."""
    try:
        session_file = os.path.join(PROJECT_ROOT, ".last_session")
        with open(session_file, "w") as f:
            f.write(json.dumps({
                "resource_id": resource_id,
                "session_id": session_id,
                "timestamp": time.time(),
                "created": time.ctime()
            }))
        print(f"Session information saved to {session_file}")
    except Exception as e:
        print(f"Warning: Could not save session info: {e}")


def load_session_info():
    """Load session info from a file."""
    try:
        session_file = os.path.join(PROJECT_ROOT, ".last_session")
        if os.path.exists(session_file):
            with open(session_file, "r") as f:
                data = json.loads(f.read())
                
                # Check if the session is less than 24 hours old (sessions typically expire)
                if (time.time() - data.get("timestamp", 0)) < 86400:  # 24 hours in seconds
                    print(f"Loaded saved session from {data.get('created')}")
                    return data.get("resource_id"), data.get("session_id")
    except Exception as e:
        print(f"Warning: Could not load session info: {e}")
    
    return None, None


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Test the Customer Service Agent")
    parser.add_argument("--session-id", help="Use an existing session ID")
    parser.add_argument("--resource-id", help="Use a specific resource ID")
    parser.add_argument("--agent-id", help="Use a specific agent ID (will construct resource ID)")
    parser.add_argument("--message", help="Send a specific message and exit")
    parser.add_argument("--test", choices=["basic", "weather", "firestore", "all"], default="all", help="Run specific test(s)")
    parser.add_argument("--select-agent", action="store_true", help="Interactive agent selection")
    parser.add_argument("--use-last-session", action="store_true", help="Use the last saved session if available")
    parser.add_argument("--save-session", action="store_true", help="Save the session for future use")
    
    args = parser.parse_args()
    
    # Determine resource ID and session ID to use
    resource_id = args.resource_id
    session_id = args.session_id
    
    # If agent ID is provided, construct resource ID
    if args.agent_id and not resource_id:
        resource_id = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{args.agent_id}"
    
    # Try to load saved session if requested
    if args.use_last_session and not (resource_id and session_id):
        saved_resource_id, saved_session_id = load_session_info()
        if saved_resource_id and saved_session_id:
            if not resource_id:
                resource_id = saved_resource_id
            if not session_id:
                session_id = saved_session_id
    
    # Allow interactive agent selection if requested
    if args.select_agent:
        selected_agent = select_agent_interactive()
        if selected_agent:
            resource_id = selected_agent["resource_id"]
    
    # If a message is provided, just send it and exit
    if args.message:
        # We need a session ID to send a message
        if not session_id:
            print("Creating a new session...")
            session_id = create_session(resource_id)
            if not session_id:
                print("Failed to create a session. Cannot send message.")
                return 1
        
        response = send_message(session_id, args.message, resource_id)
        if response:
            print("\nResponse from agent:")
            print("==================")
            print(response)
            print("==================")
            
            # Save session if requested
            if args.save_session:
                save_session_info(resource_id, session_id)
                
            return 0
        return 1
    
    # For tests, check if we need a new session
    if not session_id:
        # We'll create a session during test execution
        pass
    
    # Run the specified tests
    result = False
    if args.test == "basic":
        result = test_basic_interaction(session_id, resource_id)
    elif args.test == "weather":
        result = test_weather_integration(session_id, resource_id)
    elif args.test == "firestore":
        result = test_firestore_integration(session_id, resource_id)
    else:  # all tests
        result = run_all_tests(session_id, resource_id)
        
    # Save session if requested and successful
    if args.save_session and session_id:
        save_session_info(resource_id, session_id)
    
    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())