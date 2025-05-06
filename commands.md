# ADK Short Bot Commands

This document contains the commands used to deploy, manage, and interact with the ADK Short Bot on Vertex AI.

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

```bash
# Deploy the agent to Vertex AI
poetry run deploy-remote --create

# List all deployments
poetry run deploy-remote --list

# Create a session
poetry run deploy-remote --create_session --resource_id=your-resource-id

# List sessions for a specific deployment
poetry run deploy-remote --list_sessions --resource_id=your-resource-id

# Get details of a specific session
poetry run deploy-remote --get_session --resource_id=your-resource-id --session_id=your-session-id

# Send a message to shorten
poetry run deploy-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="Shorten this message: Hello, how are you doing today? So far, I've made breakfast today, walked dogs, and went to work."

# Delete a deployment
poetry run deploy-remote --delete --resource_id=your-resource-id
```

## Current Deployment Information

Our current deployment has the following details:

- **Resource ID**: `projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976`
- **Project**: `simple-agent-project`
- **Region**: `us-central1`
- **Python Version**: 3.11

Example command to create a session with our current deployment:

```bash
poetry run deploy-remote --create_session --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976
```

Example command to send a message:

```bash
poetry run deploy-remote --send --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976 --session_id=YOUR_SESSION_ID --message="Shorten this message: I woke up this morning feeling great, had my usual coffee and breakfast, then took my dog for a long walk in the park where we met some friends, before heading to the office for a busy day of meetings and emails."
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

# Get details for a specific agent
./list_agents.sh --id 516304272124542976

# List sessions for an agent
./list_sessions.sh --agent 516304272124542976

# Get details for a specific session
./list_sessions.sh --agent 516304272124542976 --session YOUR_SESSION_ID
```