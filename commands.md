# ADK Agents Commands

This document contains the commands used to deploy, manage, and interact with ADK agents on Vertex AI.

## Environment Setup

```bash
# Install dependencies using Poetry
poetry install

# Activate the virtual environment
source $(poetry env info --path)/bin/activate

# For Python 3.12 compatibility (if using Python 3.13+)
python3.12 -m venv .venv-py312
source .venv-py312/bin/activate
pip install poetry
poetry env use .venv-py312/bin/python
poetry install
```

## Local Deployment

```bash
# Create a new local session
poetry run deploy-local --create_session

# List all local sessions
poetry run deploy-local --list_sessions

# Get details of a specific session
poetry run deploy-local --get_session --session_id=your-session-id

# Send a message to shorten
poetry run deploy-local --send --session_id=your-session-id --message="Shorten this message: Hello, how are you doing today?"
```

## Remote Deployment on Vertex AI

### Short Bot

```bash
# Deploy the Short Bot to Vertex AI
poetry run deploy-short-remote --create

# List all deployments
poetry run deploy-short-remote --list

# Create a session
poetry run deploy-short-remote --create_session --resource_id=your-resource-id

# List sessions for a specific deployment
poetry run deploy-short-remote --list_sessions --resource_id=your-resource-id

# Get details of a specific session
poetry run deploy-short-remote --get_session --resource_id=your-resource-id --session_id=your-session-id

# Send a message to shorten
poetry run deploy-short-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="Shorten this message: Hello, how are you doing today? So far, I've made breakfast today, walked dogs, and went to work."

# Delete a deployment
poetry run deploy-short-remote --delete --resource_id=your-resource-id
```

### Weather Agent

```bash
# Deploy the Weather Agent to Vertex AI
poetry run deploy-weather-remote --create

# List all deployments
poetry run deploy-weather-remote --list

# Create a session
poetry run deploy-weather-remote --create_session --resource_id=your-resource-id

# List sessions for a specific deployment
poetry run deploy-weather-remote --list_sessions --resource_id=your-resource-id

# Get details of a specific session
poetry run deploy-weather-remote --get_session --resource_id=your-resource-id --session_id=your-session-id

# Send a message to get weather information
poetry run deploy-weather-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="What's the weather forecast for Tokyo for the next 3 days?"

# Delete a deployment
poetry run deploy-weather-remote --delete --resource_id=your-resource-id
```

## Current Deployment Information

### Short Bot

- **Resource ID**: `projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976`
- **Project**: `simple-agent-project`
- **Region**: `us-central1`
- **Python Version**: 3.11

Example command to create a session:

```bash
poetry run deploy-short-remote --create_session --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976
```

Example command to send a message:

```bash
poetry run deploy-short-remote --send --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976 --session_id=YOUR_SESSION_ID --message="Shorten this message: I woke up this morning feeling great, had my usual coffee and breakfast, then took my dog for a long walk in the park where we met some friends, before heading to the office for a busy day of meetings and emails."
```

### Weather Agent

- **Resource ID**: `projects/62704333356/locations/us-central1/reasoningEngines/6803329351933755392`
- **Project**: `simple-agent-project`
- **Region**: `us-central1`
- **Python Version**: 3.12

Example command to create a session:

```bash
poetry run deploy-weather-remote --create_session --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/6803329351933755392
```

Example command to send a message:

```bash
poetry run deploy-weather-remote --send --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/6803329351933755392 --session_id=YOUR_SESSION_ID --message="What's the weather forecast for London for the next 5 days?"
```

## Cleanup

```bash
# Run cleanup script to remove all deployments
poetry run cleanup
```

## Custom Management Scripts

We've also created custom scripts for managing the deployments directly via the Vertex AI API:

```bash
# List all agents
./list_agents.sh

# Get details for the Short Bot
./list_agents.sh --id 516304272124542976

# Get details for the Weather Agent
./list_agents.sh --id 6803329351933755392

# List sessions for the Short Bot
./list_sessions.sh --agent 516304272124542976

# List sessions for the Weather Agent
./list_sessions.sh --agent 6803329351933755392

# Get details for a specific session (replace with your session ID)
./list_sessions.sh --agent 516304272124542976 --session YOUR_SESSION_ID
```