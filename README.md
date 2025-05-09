# ADK Agents

A collection of Python-based agents using Google's Agent Development Kit (ADK) and Vertex AI.

## Included Agents

1. **Short Bot** - An agent that shortens messages while maintaining their core meaning
2. **Weather Agent** - An agent that provides weather forecasts for locations around the world
3. **Customer Service Agent** - An agent that helps customers with product recommendations, order management, and service scheduling for Cymbal Home & Garden

## Technical Details

### Environment Specifications
- **Python Version**: 3.12.10 (required for Vertex AI Agent Engine)
- **Vertex AI SDK Version**: 1.92.0
- **Google ADK Version**: 0.2.0
- **Last Updated**: May 2025

### Key Dependencies
- google-cloud-aiplatform[adk,agent_engines]==1.92.0
- google-adk>=0.2.0
- pydantic>=2.0.0
- pydantic-settings==2.8.1
- google-cloud-firestore>=2.16.1
- requests>=2.31.0
- python-dotenv>=1.0.0
- flask>=2.0.0

### Production Deployment IDs
- **Truck Sharing Agent**: projects/843958766652/locations/us-central1/reasoningEngines/1369314189046185984
- **Customer Service Agent**: projects/843958766652/locations/us-central1/reasoningEngines/2753748861997547520

## Prerequisites

- Python 3.12+
- Poetry (Python package manager)
- Google Cloud account with Vertex AI API enabled
- Google Cloud CLI (`gcloud`) installed and authenticated
  - Follow the [official installation guide](https://cloud.google.com/sdk/docs/install) to install gcloud
  - After installation, run `gcloud init` and `gcloud auth login`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/eugene-goldberg/adk-agent.git
cd adk-agent
```

2. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install project dependencies:
```bash
poetry install
```

4. Activate the virtual environment:
```bash
source $(poetry env info --path)/bin/activate
```

## Configuration

1. Create a `.env` file in the project root with the following variables:
```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=pickuptruckapp
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_STAGING_BUCKET=gs://run-sources-pickuptruckapp-us-central1

# OpenWeatherMap API key (for Weather Agent)
OPENWEATHERMAP_API_KEY=your-api-key
```

2. Set up Google Cloud authentication:
```bash
gcloud auth login
gcloud config set project pickuptruckapp
gcloud auth application-default set-quota-project pickuptruckapp
```

3. Enable required APIs:
```bash
gcloud services enable aiplatform.googleapis.com firestore.googleapis.com
```

4. Set up Firestore database (if it doesn't exist):
```bash
gcloud firestore databases create --location=nam5
```

5. Grant Firestore permissions to the Vertex AI service account:
```bash
gcloud projects add-iam-policy-binding pickuptruckapp \
  --member="serviceAccount:service-843958766652@gcp-sa-aiplatform-re.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

6. Get an OpenWeatherMap API key:
   - Register for a free account at [OpenWeatherMap](https://openweathermap.org/)
   - Navigate to the API Keys section in your account
   - Create a new API key
   - Add the key to your `.env` file as `OPENWEATHERMAP_API_KEY`
   - Note: The Weather Agent will use mock data if no API key is provided

## Usage

### Short Bot

#### Local Testing

1. Create a new session:
```bash
poetry run deploy-short-local --create_session
```

2. List all sessions:
```bash
poetry run deploy-short-local --list_sessions
```

3. Get details of a specific session:
```bash
poetry run deploy-short-local --get_session --session_id=your-session-id
```

4. Send a message to shorten:
```bash
poetry run deploy-short-local --send --session_id=your-session-id --message="Shorten this message: Hello, how are you doing today?"
```

#### Remote Deployment

1. Deploy the agent:
```bash
poetry run deploy-short-remote --create
```

2. Create a session:
```bash
poetry run deploy-short-remote --create_session --resource_id=your-resource-id
```

3. List sessions:
```bash
poetry run deploy-short-remote --list_sessions --resource_id=your-resource-id
```

4. Send a message:
```bash
poetry run deploy-short-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="Hello, how are you doing today? So far, I've made breakfast today, walked dogs, and went to work."
```

### Weather Agent

The Weather Agent provides accurate weather forecasts for locations around the world using the OpenWeatherMap API.

#### Features

- Current weather conditions including temperature, humidity, and wind speed
- Multi-day forecasts with high/low temperatures
- Detailed weather descriptions and recommendations
- Support for cities worldwide
- Real weather data with OpenWeatherMap API integration (uses mock data as a fallback)

#### Local Testing

1. Create a new session:
```bash
poetry run deploy-weather-local --create_session
```

2. List all sessions:
```bash
poetry run deploy-weather-local --list_sessions
```

3. Get details of a specific session:
```bash
poetry run deploy-weather-local --get_session --session_id=your-session-id
```

4. Send a message for weather information:
```bash
poetry run deploy-weather-local --send --session_id=your-session-id --message="What's the weather like in London today?"
```

5. Ask for multiple days forecast:
```bash
poetry run deploy-weather-local --send --session_id=your-session-id --message="What will the weather be like in Tokyo for the next 5 days?"
```

#### Remote Deployment

1. Deploy the agent:
```bash
poetry run deploy-weather-remote --create
```

2. Create a session:
```bash
poetry run deploy-weather-remote --create_session --resource_id=your-resource-id
```

3. List sessions:
```bash
poetry run deploy-weather-remote --list_sessions --resource_id=your-resource-id
```

4. Send a message:
```bash
poetry run deploy-weather-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="What will the weather be like in Tokyo for the next 5 days?"
```

### Customer Service Agent

The Customer Service Agent helps customers with product recommendations, order management, and service scheduling for Cymbal Home & Garden. It includes Firestore integration for managing customer bookings and records, as well as Weather integration for providing weather-based gardening advice.

#### Features

- Product identification and recommendations based on customer needs and climate
- Order management and cart modifications
- Appointment scheduling with Firestore persistence
- Discount approvals with manager validation
- Firestore database integration for:
  - Creating and managing bookings
  - Retrieving customer records
  - Tracking service appointments
  - Storing customer preferences
  - Persistent data across sessions
- Weather integration for:
  - Current weather conditions and forecasts
  - Weather-based gardening recommendations
  - Optimal planting time suggestions
  - Climate-appropriate plant selection

#### Local Testing

1. Create a new session:
```bash
poetry run deploy-cs-local --create_session
```

2. List all sessions:
```bash
poetry run deploy-cs-local --list_sessions
```

3. Get details of a specific session:
```bash
poetry run deploy-cs-local --get_session --session_id=your-session-id
```

4. Send a message to the customer service agent:
```bash
poetry run deploy-cs-local --send --session_id=your-session-id --message="I'm looking for a lawnmower recommendation."
```

5. Test Firestore integration:
```bash
poetry run deploy-cs-local --send --session_id=your-session-id --message="Show me all my bookings from the database."
poetry run deploy-cs-local --send --session_id=your-session-id --message="Create a new booking for garden planting on June 15th from 2-5pm."
```

6. Test Weather integration:
```bash
poetry run deploy-cs-local --send --session_id=your-session-id --message="What's the weather forecast for Las Vegas for the next 3 days?"
poetry run deploy-cs-local --send --session_id=your-session-id --message="Based on the weather, what plants would work well in my garden this weekend?"
```

7. Interactive testing:
```bash
python test_customer_service.py --mode=local --session_id=your-session-id --interactive
```

#### Remote Deployment

1. Deploy the agent:
```bash
poetry run deploy-cs-remote --create
```

2. Create a session:
```bash
poetry run deploy-cs-remote --create_session --resource_id=your-resource-id
```

3. List sessions:
```bash
poetry run deploy-cs-remote --list_sessions --resource_id=your-resource-id
```

4. Send a message:
```bash
poetry run deploy-cs-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="I'm looking for plants suitable for a desert climate."
```

5. Test Firestore integration:
```bash
# Show all bookings in the database
poetry run deploy-cs-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="Show me all bookings in the Firestore database."

# Create a new booking
poetry run deploy-cs-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="Create a new booking for me for planting service on June 15th."

# Store with a specific ID
poetry run deploy-cs-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="Store this booking in the database with ID june-planting-2025."

# Retrieve a specific booking
poetry run deploy-cs-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="Get the details of booking june-planting-2025."
```

6. Test Weather integration:
```bash
# Get weather forecast
poetry run deploy-cs-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="What's the weather forecast for Las Vegas for the next 5 days?"

# Get climate-based gardening advice
poetry run deploy-cs-remote --send --resource_id=your-resource-id --session_id=your-session-id --message="I'm planning to plant some drought-resistant plants this weekend. Will the weather be suitable, and what do you recommend?"
```

7. Interactive testing:
```bash
python test_customer_service.py --mode=remote --resource_id=your-resource-id --session_id=your-session-id --interactive
```

#### Firestore and Weather Integration Testing

The integrations can be directly tested using the provided test scripts:

```bash
# Test connection to Firestore
python customer_service/test_firestore_agent.py

# Test live Firestore operations (CRUD)
python customer_service/test_firestore_live.py

# Test Firestore integration with the Customer Service agent
python customer_service/test_firestore_direct.py

# Test Weather integration
python weather_agent/test_weather_api.py
```

### Cleanup

To delete any deployment:
```bash
poetry run deploy-short-remote --delete --resource_id=your-resource-id
# or
poetry run deploy-weather-remote --delete --resource_id=your-resource-id
```

## Project Structure

```
adk-agent/
├── adk_short_bot/             # Short Bot package directory
│   ├── __init__.py
│   ├── agent.py              # Short Bot implementation
│   ├── prompt.py             # Short Bot prompt templates
│   └── tools/                # Short Bot tools
│       ├── __init__.py
│       └── character_counter.py
├── weather_agent/            # Weather Agent package directory
│   ├── __init__.py
│   ├── agent.py              # Weather Agent implementation
│   ├── prompt.py             # Weather Agent prompt templates
│   └── tools/                # Weather Agent tools
│       ├── __init__.py
│       └── weather_api.py
├── customer_service/         # Customer Service Agent package directory
│   ├── __init__.py
│   ├── agent.py              # Customer Service Agent implementation
│   ├── config.py             # Configuration settings
│   ├── prompts.py            # Customer Service Agent prompt templates
│   ├── entities/             # Entity definitions
│   │   ├── __init__.py
│   │   └── customer.py       # Customer entity model
│   ├── firestore_agent/      # Firestore integration
│   │   ├── __init__.py
│   │   ├── agent.py          # Firestore Agent implementation
│   │   ├── prompts.py        # Firestore Agent prompts
│   │   └── tools.py          # Firestore database operations
│   ├── shared_libraries/     # Shared utilities
│   │   ├── __init__.py
│   │   └── callbacks.py      # Agent callbacks
│   ├── tools/                # Customer Service Agent tools
│   │   ├── __init__.py
│   │   └── tools.py          # Tool implementations
│   ├── test_firestore_agent.py # Tests for Firestore integration
│   ├── test_firestore_live.py  # Live testing of Firestore operations
│   └── test_firestore_direct.py # Direct testing of Firestore integration
├── deployment/               # Deployment scripts
│   ├── local.py              # Short Bot local testing script
│   ├── remote.py             # Short Bot remote deployment script
│   ├── weather_local.py      # Weather Agent local testing script
│   ├── weather_remote.py     # Weather Agent remote deployment script
│   ├── customer_service_local.py  # Customer Service Agent local testing script
│   ├── customer_service_remote.py # Customer Service Agent remote deployment script
│   └── cleanup.py            # Cleanup script for deployments
├── test_customer_service.py  # Interactive testing script for Customer Service Agent
├── list_agents.sh            # Helper script to list agents
├── list_sessions.sh          # Helper script to list sessions
├── commands.md               # Documentation of Poetry commands
├── .env                      # Environment variables
├── poetry.lock               # Poetry lock file
└── pyproject.toml            # Project configuration
```

## Development

To add new features or modify existing ones:

1. Make your changes in the relevant files
2. Test locally using the local deployment script
3. Deploy to remote using the remote deployment script
4. Update documentation as needed

## Troubleshooting

1. If you encounter authentication issues:
   - Ensure you're logged in with `gcloud auth login`
   - Verify your project ID and location in `.env`
   - Set your application default credentials: `gcloud auth application-default set-quota-project pickuptruckapp`
   - Check that all required APIs are enabled: Vertex AI, Firestore

2. If deployment fails:
   - Check the staging bucket exists and is accessible
   - Verify all required environment variables are set
   - Ensure you have the necessary permissions in your Google Cloud project
   - Verify the bucket is in the correct location (us-central1)

3. If Firestore integration fails:
   - Check that the Firestore database is created in the project
   - Verify the service account has the necessary permissions
   - Ensure your ADC is properly configured for the pickuptruckapp project

4. If Weather integration returns mock data:
   - Check that you have provided a valid OpenWeatherMap API key in your .env file
   - Verify the API key has the necessary access to the weather endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your chosen license]
