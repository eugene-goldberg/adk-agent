# Testing ADK Agents

This document provides detailed instructions and examples for testing the ADK agents deployed on Vertex AI.

## Table of Contents

- [General Testing Process](#general-testing-process)
- [Short Bot Testing](#short-bot-testing)
- [Weather Agent Testing](#weather-agent-testing)
- [Customer Service Agent Testing](#customer-service-agent-testing)
- [Error Handling Testing](#error-handling-testing)
- [Local Testing](#local-testing)
- [Testing with ADK CLI](#testing-with-adk-cli)

## General Testing Process

Testing a deployed agent is a two-step process:

1. **Create a session** - First, create a session to get a session ID
2. **Send messages** - Then use the session ID to send messages to the agent

This approach allows for stateful conversations and session management.

## Short Bot Testing

The Short Bot condenses messages while maintaining their core meaning.

### Step 1: Create a session

```bash
# Activate the appropriate Python environment
source .venv-py312/bin/activate

# Create a session with the Short Bot
python deployment/remote.py --create_session --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976

# Note the session ID from the output, for example: 6802454690433859584
```

### Step 2: Send test messages

```bash
# Test with a personal message
python deployment/remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976 \
  --session_id=YOUR_SESSION_ID \
  --message="Shorten this message: I woke up early this morning feeling well-rested and energized. After enjoying a hearty breakfast of scrambled eggs and toast, I took my dog for a long walk in the park where we encountered several other dog owners and their pets. Once I returned home, I prepared for a busy workday that included three important meetings and numerous emails that required my immediate attention."

# Test with a business message
python deployment/remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976 \
  --session_id=YOUR_SESSION_ID \
  --message="Shorten this message: The annual shareholders meeting will be held on Tuesday, June 15th, 2026, at 10:00 AM Eastern Time at the corporate headquarters located at 123 Business Avenue, New York, NY. All shareholders are encouraged to attend in person, but there will also be an option to participate virtually through our secure online platform. Please bring your shareholder identification and a valid photo ID if attending in person. The meeting agenda includes a review of the company's financial performance for the fiscal year 2025, voting on proposed changes to the board of directors, and a discussion of the company's strategic plan for the next five years."

# Test with a technical message
python deployment/remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976 \
  --session_id=YOUR_SESSION_ID \
  --message="Shorten this message: The new software update includes several important security patches that address recently discovered vulnerabilities, along with performance improvements for memory usage and battery life. Users are strongly encouraged to install this update as soon as possible to ensure their devices remain protected. Additionally, the update introduces a redesigned user interface with improved navigation and accessibility features, as well as integration with our new cloud backup service that provides automatic syncing across all your connected devices."
```

## Weather Agent Testing

The Weather Agent provides weather forecasts for locations around the world.

### Step 1: Create a session

```bash
# Activate the appropriate Python environment
source .venv-py312/bin/activate

# Create a session with the Weather Agent
python deployment/weather_remote.py --create_session --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/6803329351933755392

# Note the session ID from the output, for example: 8657937736910503936
```

### Step 2: Send test messages

```bash
# Test basic weather query
python deployment/weather_remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/6803329351933755392 \
  --session_id=YOUR_SESSION_ID \
  --message="What's the weather like in Tokyo today?"

# Test multi-day forecast
python deployment/weather_remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/6803329351933755392 \
  --session_id=YOUR_SESSION_ID \
  --message="What's the weather forecast for London for the next 5 days?"

# Test comparison between cities
python deployment/weather_remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/6803329351933755392 \
  --session_id=YOUR_SESSION_ID \
  --message="Can you compare the weather in New York and Paris today?"

# Test with various supported cities
python deployment/weather_remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/6803329351933755392 \
  --session_id=YOUR_SESSION_ID \
  --message="What's the weather like in Berlin right now?"
```

## Customer Service Agent Testing

The Customer Service Agent helps customers with gardening advice, product recommendations, order management, and service scheduling. It includes Firestore integration for managing customer bookings and data, as well as Weather integration for providing weather-based gardening advice.

### Step 1: Create a session

```bash
# Activate the appropriate Python environment
source .venv-py312/bin/activate

# Create a session with the Customer Service Agent
python deployment/customer_service_remote.py --create_session --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008

# Note the session ID from the output
```

### Step 2: Send test messages

```bash
# Test basic greeting and gardening advice
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Hello, I'm looking for some gardening advice for my home in Las Vegas."

# Test product recommendations
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Can you recommend plants that would do well in a hot, dry climate?"

# Test cart management
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Can you show me what's in my cart?"

# Test service scheduling
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="I'm interested in your planting services. What are the available times?"

# Test discount approval
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="I saw this fertilizer for $5 cheaper at another store. Can you match that price?"
```

### Step 3: Test Firestore integration

```bash
# Test listing bookings from Firestore
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Show me all bookings in the Firestore database"

# Test creating a new booking in Firestore
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Create a new booking for planting service on June 15th, 2025 from 2pm to 5pm."

# Test storing a booking with a specific ID
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Store this booking in the database with ID june-planting-2025"

# Test retrieving specific booking details
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Get the details of booking june-planting-2025"
```

### Step 4: Test Weather integration

```bash
# Test basic weather query
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="What's the weather forecast for Las Vegas for the next 3 days?"

# Test weather-based gardening advice
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="I'm planning to plant some drought-resistant plants this weekend. Will the weather be suitable, and what do you recommend?"

# Test weather comparison for plant selection
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="I'm trying to decide whether to plant now or wait until next week. Can you compare the weather for both time periods and advise me?"
```

## Firestore Integration Testing

The Customer Service Agent includes integration with Firestore for data storage and retrieval. Here are detailed tests for this integration.

### Direct Firestore Testing

```bash
# Test basic Firestore agent functionality
python customer_service/test_firestore_agent.py

# Test all Firestore operations (CRUD) against a live database
python customer_service/test_firestore_live.py

# Test the Customer Service agent's direct integration with Firestore
python customer_service/test_firestore_direct.py
```

## Weather Integration Testing

The Customer Service Agent includes integration with the Weather Agent to provide climate-based gardening advice.

### Weather Query Examples

```bash
# Test basic weather forecasting
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="What's the weather going to be like in Phoenix next week?"

# Test weather-based plant recommendations
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Which flowers would thrive with the current weather in Las Vegas?"

# Test gardening planning based on weather
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="When would be the best time to plant my tomatoes based on the weather forecast?"
```

### Weather API Configuration

For real weather data (instead of mock data), provide an OpenWeatherMap API key in your `.env` file:

```bash
# Add this to your .env file
OPENWEATHERMAP_API_KEY=your_api_key_here
```

You can obtain a free API key by registering at [OpenWeatherMap](https://openweathermap.org/).

### Firestore Operation Examples

The Firestore integration supports the following operations:

1. **Read Operation**:
```bash
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Show me booking with ID booking456"
```

2. **Write Operation**:
```bash
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Create a new booking for planting service on June 15th, 2025 from 1pm to 4pm"
```

3. **Update Operation**:
```bash
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Update my booking to include special instructions: need help with planting roses"
```

4. **Query Operation**:
```bash
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Show me all my confirmed bookings"
```

5. **Delete Operation**:
```bash
python deployment/customer_service_remote.py --send \
  --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 \
  --session_id=YOUR_SESSION_ID \
  --message="Please cancel and delete my booking for June 15th"
```

### Firestore Permission Setup

When deploying to Vertex AI, ensure the service account has the necessary Firestore permissions:

```bash
# Grant Firestore permissions to the service account
gcloud projects add-iam-policy-binding pickuptruckapp \
  --member="serviceAccount:service-843958766652@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

# For read-only access, you can use:
gcloud projects add-iam-policy-binding pickuptruckapp \
  --member="serviceAccount:service-843958766652@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/datastore.viewer"
```

## Error Handling Testing

Test how the agents handle errors and edge cases.

### Short Bot Error Testing

```bash
# Test with an empty message
python deployment/remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976 \
  --session_id=YOUR_SESSION_ID \
  --message="Shorten this message: "

# Test with a very short message that doesn't need shortening
python deployment/remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/516304272124542976 \
  --session_id=YOUR_SESSION_ID \
  --message="Shorten this message: Hello world."
```

### Weather Agent Error Testing

```bash
# Test with an invalid location
python deployment/weather_remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/6803329351933755392 \
  --session_id=YOUR_SESSION_ID \
  --message="What's the weather like in InvalidCity today?"

# Test with a vague or ambiguous location
python deployment/weather_remote.py --send \
  --resource_id=projects/62704333356/locations/us-central1/reasoningEngines/6803329351933755392 \
  --session_id=YOUR_SESSION_ID \
  --message="What's the weather like downtown?"
```

## Local Testing

For development and testing without deploying to Vertex AI, you can use local deployment:

### Short Bot Local Testing

```bash
# Create a local session
python deployment/local.py --create_session

# Send a test message with the session ID
python deployment/local.py --send --session_id=YOUR_LOCAL_SESSION_ID --message="Shorten this message: Your test message here."
```

### Weather Agent Local Testing

```bash
# Create a local session
python deployment/weather_local.py --create_session

# Send a test message with the session ID
python deployment/weather_local.py --send --session_id=YOUR_LOCAL_SESSION_ID --message="What's the weather like in Paris today?"
```

### Customer Service Agent Local Testing

```bash
# Create a local session
python deployment/customer_service_local.py --create_session

# Send a test message with the session ID
python deployment/customer_service_local.py --send --session_id=YOUR_LOCAL_SESSION_ID --message="Hello, I'm looking for gardening advice for desert plants."
```

## Testing with ADK CLI

The Google ADK Command Line Interface provides additional tools for testing agents locally:

### Install ADK CLI

```bash
pip install google-adk
```

### Test with Interactive CLI

```bash
# Test the Weather Agent interactively
cd /Users/eugene/dev/ai/agents/deploy-adk-agent-engine
export PYTHONPATH=$PYTHONPATH:$(pwd)
adk run weather_agent

# When prompted, enter messages like:
# "What's the weather like in Tokyo today?"
# "What's the weather forecast for London for the next 3 days?"
```

```bash
# Test the Customer Service Agent interactively
cd /Users/eugene/dev/ai/agents/deploy-adk-agent-engine
export PYTHONPATH=$PYTHONPATH:$(pwd)
adk run customer_service

# When prompted, enter messages like:
# "Hello, I'm looking for some gardening advice for Las Vegas."
# "Can you recommend drought-resistant plants?"
# "Can you show me what's in my cart?"
```

### Test with Web UI

```bash
# Start a web interface for testing the Weather Agent
cd /Users/eugene/dev/ai/agents/deploy-adk-agent-engine
export PYTHONPATH=$PYTHONPATH:$(pwd)
adk web weather_agent

# Then open http://localhost:8000 in your browser
```

```bash
# Start a web interface for testing the Customer Service Agent
cd /Users/eugene/dev/ai/agents/deploy-adk-agent-engine
export PYTHONPATH=$PYTHONPATH:$(pwd)
adk web customer_service

# Then open http://localhost:8000 in your browser
```

## Viewing Deployment Information

You can check details about your agent deployments using custom scripts:

```bash
# List all agents
./list_agents.sh

# Get details for the Short Bot
./list_agents.sh --id 516304272124542976

# Get details for the Weather Agent
./list_agents.sh --id 6803329351933755392

# Get details for the Customer Service Agent
./list_agents.sh --id 3893159567722283008

# List sessions for the Weather Agent
./list_sessions.sh --agent 6803329351933755392

# List sessions for the Customer Service Agent
./list_sessions.sh --agent 3893159567722283008
```

## Interactive Testing

For a more convenient interactive testing experience, you can use the test_customer_service.py script:

```bash
# Interactive local testing
python test_customer_service.py --mode=local --session_id=YOUR_LOCAL_SESSION_ID --interactive

# Interactive remote testing
python test_customer_service.py --mode=remote --resource_id=projects/843958766652/locations/us-central1/reasoningEngines/3893159567722283008 --session_id=YOUR_SESSION_ID --interactive
```

In interactive mode, you can enter messages one by one and see the responses, making it easier to test a full conversation flow.