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

## Firestore Integration

The Customer Service Agent includes Firestore integration for managing customer data and bookings in the pickuptruckapp GCP project.

### Firestore Setup and Configuration

```bash
# Set your Google Cloud project
gcloud config set project pickuptruckapp

# Set your application default credentials
gcloud auth application-default set-quota-project pickuptruckapp

# Create Firestore database (if it doesn't exist)
gcloud firestore databases create --location=nam5

# Grant Firestore permissions to the Vertex AI service account
gcloud projects add-iam-policy-binding pickuptruckapp \
  --member="serviceAccount:service-843958766652@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### Testing Firestore Integration

```bash
# Test basic Firestore agent functionality
python customer_service/test_firestore_agent.py

# Test Firestore operations against a live database
python customer_service/test_firestore_live.py

# Test the Customer Service agent's Firestore integration
python customer_service/test_firestore_direct.py
```

### Firestore Operations Examples

The Firestore integration supports the following operations:

```bash
# Create a session
poetry run deploy-cs-remote --create_session --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008

# List all bookings
poetry run deploy-cs-remote --send --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --message="Show me all bookings in the Firestore database"

# Create a booking
poetry run deploy-cs-remote --send --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --message="Create a new booking for planting service on June 15th, 2025 from 2pm to 5pm"

# Store a booking with specific ID
poetry run deploy-cs-remote --send --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --message="Store this booking in the database with ID garden-planting-june-2025"

# Read a specific booking
poetry run deploy-cs-remote --send --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --message="Get the details of booking garden-planting-june-2025"

# Update a booking
poetry run deploy-cs-remote --send --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --message="Update my booking to include special instructions: need help with planting roses"

# Query bookings by status
poetry run deploy-cs-remote --send --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --message="Show me all my confirmed bookings"

# Delete a booking
poetry run deploy-cs-remote --send --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --message="Please cancel and delete my booking for June 15th"
```

## Weather Integration

The Customer Service Agent also includes Weather integration for providing weather-based gardening advice.

### Weather API Configuration

Add your OpenWeatherMap API key to your `.env` file:

```bash
# Add to .env
OPENWEATHERMAP_API_KEY=your_api_key_here
```

### Weather Operations Examples

```bash
# Get basic weather forecast
poetry run deploy-cs-remote --send --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --message="What's the weather forecast for Las Vegas for the next 3 days?"

# Get weather-based gardening advice
poetry run deploy-cs-remote --send --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --message="I'm planning to plant some drought-resistant plants this weekend. Will the weather be suitable, and what do you recommend?"

# Get climate-appropriate plant suggestions
poetry run deploy-cs-remote --send --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --message="Which flowers would thrive in Phoenix with the current weather conditions?"
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

# Get details for the Customer Service Agent
./list_agents.sh --id 2852828053799698432

# List sessions for the Short Bot
./list_sessions.sh --agent 516304272124542976

# List sessions for the Weather Agent
./list_sessions.sh --agent 6803329351933755392

# List sessions for the Customer Service Agent
./list_sessions.sh --agent 2852828053799698432

# Get details for a specific session (replace with your session ID)
./list_sessions.sh --agent 2852828053799698432 --session YOUR_SESSION_ID
```