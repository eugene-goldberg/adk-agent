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
    print("\n1. Test with a simple weather query:")
    print("```bash")
    print("adk test --agent weather_agent.agent.weather_agent \"What's the weather like in Tokyo today?\"")
    print("```")
    print("\n2. Test with a multi-day forecast query:")
    print("```bash")
    print("adk test --agent weather_agent.agent.weather_agent \"What's the weather forecast for London for the next 3 days?\"")
    print("```")
    print("\n3. Test with an invalid location:")
    print("```bash")
    print("adk test --agent weather_agent.agent.weather_agent \"What's the weather like in InvalidCity today?\"")
    print("```")
    print("\n## Remote Deployment")
    print("\nAfter testing, you can deploy the Weather Agent to Vertex AI by running:")
    print("```bash")
    print("poetry run deploy-weather-remote --create")
    print("```")
    
if __name__ == "__main__":
    show_instructions()