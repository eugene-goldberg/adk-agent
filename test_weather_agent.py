"""
Instructions for testing the Weather Agent using the Google ADK CLI.

This file provides instructions rather than direct testing, since the ADK CLI 
is the recommended way to test agents locally before deployment.
"""

def show_instructions():
    """Show instructions for testing the Weather Agent."""
    print("# Testing the Weather Agent")
    print("\nTo test the Weather Agent locally, you can use the Google ADK CLI.")
    print("Make sure you have the ADK CLI installed and configured:")
    print("\n```bash")
    print("pip install google-adk")
    print("```")
    print("\n## Testing Commands")
    print("\n1. Test with interactive CLI:")
    print("```bash")
    print("cd /Users/eugene/dev/ai/agents/deploy-adk-agent-engine")
    print("export PYTHONPATH=$PYTHONPATH:$(pwd)")
    print("adk run weather_agent")
    print("# Then type: What's the weather like in Tokyo today?")
    print("# Or: What's the weather forecast for London for the next 3 days?")
    print("```")
    print("\n2. Start a web UI for testing:")
    print("```bash")
    print("cd /Users/eugene/dev/ai/agents/deploy-adk-agent-engine")
    print("export PYTHONPATH=$PYTHONPATH:$(pwd)")
    print("adk web weather_agent")
    print("# Then open: http://localhost:8000 in your browser")
    print("```")
    print("\n## Remote Deployment")
    print("\nAfter testing, you can deploy the Weather Agent to Vertex AI by running:")
    print("```bash")
    print("poetry run deploy-weather-remote --create")
    print("```")
    
if __name__ == "__main__":
    show_instructions()